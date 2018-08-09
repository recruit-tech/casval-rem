import boto3
import json
import pytz

from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQS_SCAN_WAITING = "ScanWaiting"
SQS_SCAN_ONGOING = "ScanOngoing"
SQS_SCAN_COMPLETE = "ScanComplete"
SQS_SCAN_FAILURE = "ScanFailure"


def scan_launcher(app):
    try:
        sqs = boto3.resource("sqs")
        waiting_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_WAITING)
        ongoing_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_ONGOING)
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

            entries = []
            for message in messages:
                try:
                    body = json.loads(message.body)
                    start_at = datetime.strptime(body["start_at"], DATETIME_FORMAT)
                    start_at = start_at.replace(tzinfo=pytz.utc)
                    end_at = datetime.strptime(body["end_at"], DATETIME_FORMAT)
                    end_at = end_at.replace(tzinfo=pytz.utc)
                    if start_at <= base_time:
                        app.log.debug("message processed: " + message.message_id)
                        if end_at > base_time:
                            # ToDo: Set scan to OpenVas and get scan ID
                            body["scanner"] = {"name": "openvas", "host": "127.0.0.1", "port": 80, "id": "ID"}
                            ongoing_queue.send_message(MessageBody=json.dumps(body))
                        else:
                            body[
                                "error"
                            ] = "The scan could not be started since its completion deadline is soon or over."
                            failure_queue.send_message(MessageBody=json.dumps(body))
                        # Delete the message only when it has been processed
                        entries.append({"Id": message.message_id, "ReceiptHandle": message.receipt_handle})
                except Exception as e:
                    app.log.error(e)
                    body["error"] = str(e)
                    failure_queue.send_message(MessageBody=json.dumps(body))
            if len(entries) is not 0:
                waiting_queue.delete_messages(Entries=entries)

    except Exception as e:
        app.log.error(e)
        raise e
    return


def scan_processor(app):
    try:
        sqs = boto3.resource("sqs")
        ongoing_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_ONGOING)
        complete_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_COMPLETE)
        failure_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_FAILURE)
        jst = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tz=pytz.utc).astimezone(jst)
        while 1:
            messages = ongoing_queue.receive_messages(MaxNumberOfMessages=10)
            app.log.debug("messages obtained: " + str(len(messages)))
            if len(messages) is 0:
                break

            for message in messages:
                try:
                    body = json.loads(message.body)
                    end_at = datetime.strptime(body["end_at"], DATETIME_FORMAT)
                    end_at = end_at.replace(tzinfo=pytz.utc)
                    if end_at > now:
                        # ToDo: Check OpenVas status
                        result = True
                        if result is True:
                            complete_queue.send_message(MessageBody=message.body)
                            ongoing_queue.delete_messages(
                                Entries=[{"Id": message.message_id, "ReceiptHandle": message.receipt_handle}]
                            )
                    else:
                        # ToDo: Stop OpenVas
                        body["error"] = "The scan has been terminated since its completion deadline is over."
                        failure_queue.send_message(MessageBody=json.dumps(body))
                        ongoing_queue.delete_messages(
                            Entries=[{"Id": message.message_id, "ReceiptHandle": message.receipt_handle}]
                        )
                except Exception as e:
                    app.log.error(e)
                    body["error"] = str(e)
                    failure_queue.send_message(MessageBody=json.dumps(body))
                    ongoing_queue.delete_messages(
                        Entries=[{"Id": message.message_id, "ReceiptHandle": message.receipt_handle}]
                    )

    except Exception as e:
        app.log.error(e)
        raise e

    return
