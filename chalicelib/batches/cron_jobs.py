import json
import logging
import os
from datetime import datetime

import boto3
import pytz

from chalicelib.core.scanner import Scanner

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQS_SCAN_WAITING = "ScanWaiting"
SQS_SCAN_ONGOING = "ScanOngoing"
SQS_SCAN_COMPLETE = "ScanComplete"
SQS_SCAN_FAILURE = "ScanFailure"


def scan_launcher(app):
    try:
        sqs = boto3.resource("sqs")
        waiting_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_WAITING)
        failure_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_FAILURE)
        jst = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tz=pytz.utc).astimezone(jst)
        base_time = now.replace(minute=59, second=59, microsecond=999999)
        app.log.debug("base_time: " + str(base_time))
        while 1:
            messages = waiting_queue.receive_messages(MaxNumberOfMessages=10)
            app.log.debug("messages obtained: " + str(len(messages)))
            if len(messages) is 0:
                break

            for message in messages:
                entry = {"Id": message.message_id, "ReceiptHandle": message.receipt_handle}
                try:
                    body = json.loads(message.body)
                    start_at = datetime.strptime(body["start_at"], DATETIME_FORMAT)
                    start_at = start_at.replace(tzinfo=pytz.utc)
                    end_at = datetime.strptime(body["end_at"], DATETIME_FORMAT)
                    end_at = end_at.replace(tzinfo=pytz.utc)
                    if start_at <= base_time:
                        app.log.debug("message processed: " + message.message_id)
                        if end_at > base_time:
                            async_call(app, "async_scan_launch", {"entry": entry, "body": body})
                        else:
                            raise Exception(
                                "The scan could not be started since its completion deadline is soon or over."
                            )
                except Exception as e:
                    app.log.error(e)
                    body["error"] = str(e)
                    failure_queue.send_message(MessageBody=json.dumps(body))
                    waiting_queue.delete_messages(Entries=[entry])

    except Exception as e:
        app.log.error(e)
        raise e
    return


def async_scan_launch(event):
    try:
        entry = event["entry"]
        body = event["body"]
        sqs = boto3.resource("sqs")
        waiting_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_WAITING)
        ongoing_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_ONGOING)
        scanner = Scanner(os.environ["SCANNER"])
        session = scanner.launch(body["target"])
        body["session"] = session
        ongoing_queue.send_message(MessageBody=json.dumps(body))
        waiting_queue.delete_messages(Entries=[entry])
    except Exception as e:
        logger.warning(e)
    return None


def scan_processor(app):
    try:
        sqs = boto3.resource("sqs")
        ongoing_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_ONGOING)
        failure_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_FAILURE)
        jst = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tz=pytz.utc).astimezone(jst)
        while 1:
            messages = ongoing_queue.receive_messages(MaxNumberOfMessages=10)
            app.log.debug("messages obtained: " + str(len(messages)))
            if len(messages) is 0:
                break

            for message in messages:
                entry = {"Id": message.message_id, "ReceiptHandle": message.receipt_handle}
                try:
                    body = json.loads(message.body)
                    end_at = datetime.strptime(body["end_at"], DATETIME_FORMAT)
                    end_at = end_at.replace(tzinfo=pytz.utc)
                    if end_at > now:
                        async_call(app, "async_scan_status_check", {"entry": entry, "body": body})
                    else:
                        async_call(app, "async_scan_terminate", {"body": body})
                        raise Exception("The scan has been terminated since its completion deadline is over.")
                except Exception as e:
                    app.log.error(e)
                    body["error"] = str(e)
                    failure_queue.send_message(MessageBody=json.dumps(body))
                    ongoing_queue.delete_messages(Entries=[entry])

    except Exception as e:
        app.log.error(e)
        raise e

    return


def async_scan_status_check(event):
    try:
        logger.info("scan status check session: {session}".format(session=event["body"]["session"]))
        sqs = boto3.resource("sqs")
        body = event["body"]
        scanner = Scanner(os.environ["SCANNER"])
        status = scanner.check_status(body["session"])
        logger.info("scan status: {status}({type})".format(status=status, type=type(status)))
        if status == "complete":
            ongoing_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_ONGOING)
            complete_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_COMPLETE)
            complete_queue.send_message(MessageBody=json.dumps(body))
            ongoing_queue.delete_messages(Entries=[event["entry"]])
        elif status == "failure":
            failure_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_FAILURE)
            complete_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_COMPLETE)
            body["error"] = "scan status indicates that scan session has been failed."
            failure_queue.send_message(MessageBody=json.dumps(body))
            ongoing_queue.delete_messages(Entries=[event["entry"]])
    except Exception as e:
        logger.warning(e)
    return


def async_scan_terminate(event):
    try:
        scanner = Scanner(os.environ["SCANNER"])
        scanner.terminate(event["body"]["session"])
    except Exception as e:
        logger.warning(e)
    return None


def async_call(app, func, payload):
    func_name = "{app}-{stage}-{func}".format(app=app.app_name, stage=os.environ["STAGE"], func=func)
    lmd = boto3.client("lambda")
    lmd.invoke(FunctionName=func_name, InvocationType="Event", Payload=json.dumps(payload))
    return
