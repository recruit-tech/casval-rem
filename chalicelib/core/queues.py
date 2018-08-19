import json

import boto3


class Queue:

    SCAN_WAITING = "ScanWaiting"

    def __init__(self, queue):
        self.queue = queue

    def enqueue(self, message):
        sqs = boto3.resource("sqs")
        queue = sqs.get_queue_by_name(QueueName=self.queue)
        queue.send_message(MessageBody=(json.dumps(message)))
