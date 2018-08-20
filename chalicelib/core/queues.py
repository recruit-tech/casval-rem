import json

import boto3


class Queue:

    SCAN_PENDING = "ScanPending"
    SCAN_RUNNING = "ScanRunning"
    SCAN_STOPPED = "ScanStopped"

    MAX_NUMBER_OF_MESSAGES = 10

    def __init__(self, queue):
        self.sqs = boto3.resource("sqs")
        self.queue = self.sqs.get_queue_by_name(QueueName=queue)

    def enqueue(self, message):
        self.queue.send_message(MessageBody=(json.dumps(message)))

    def peek(self):
        return self.queue.receive_messages(MaxNumberOfMessages=Queue.MAX_NUMBER_OF_MESSAGES)

    def delete(self, entry):
        self.queue.delete_messages(Entries=[entry])

    def message_count(self):
        client = boto3.client("sqs")
        response = client.get_queue_attributes(
            QueueUrl=self.queue.url,
            AttributeNames=["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"],
        )
        message_num = response["Attributes"]["ApproximateNumberOfMessages"]
        message_num_not_visible = response["Attributes"]["ApproximateNumberOfMessagesNotVisible"]
        total_message_num = int(message_num) + int(message_num_not_visible)
        return total_message_num
