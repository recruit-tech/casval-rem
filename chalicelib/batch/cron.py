import boto3
import json
import pytz

from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQS_SCAN_WAITING = "ScanWaiting"
SQS_SCAN_ONGOING = "ScanOngoing"


def scan_scheduler(app):
    try:
        sqs = boto3.resource("sqs")
        waiting_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_WAITING)
        ongoing_queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_ONGOING)
        jst = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tz=pytz.utc).astimezone(jst)
        base_time = now.replace(minute=59, second=59, microsecond=999999)
        app.log.debug("base_time: " + str(base_time))
        while 1:
            msgs = waiting_queue.receive_messages(MaxNumberOfMessages=10)
            app.log.debug("messages obtained: " + str(len(msgs)))
            if len(msgs) is 0:
                break
            entries = []
            for msg in msgs:
                body = json.loads(msg.body)
                start_at = datetime.strptime(body["start_at"], DATETIME_FORMAT)
                start_at = start_at.replace(tzinfo=pytz.utc)
                if start_at <= base_time:
                    app.log.debug("start_at: " + str(start_at))
                    ongoing_queue.send_message(MessageBody=msg.body)
                    entries.append({"Id": msg.message_id, "ReceiptHandle": msg.receipt_handle})
                if len(entries) is not 0:
                    waiting_queue.delete_messages(Entries=entries)

    except Exception as e:
        app.log.error(e)
        raise e

    return
