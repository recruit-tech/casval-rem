import boto3
import json
import os


class SQSMock(object):

    __instance = None

    def __new__(cls, queue):
        if cls.__instance is None:
            cls.__instance = super(SQSMock, cls).__new__(cls)
            cls.__instance.__initialized = False
        else:
            cls.__instance.queue = cls.__instance.sqs.get_queue_by_name(QueueName=queue)

        return cls.__instance

    def __init__(self, queue):
        if self.__initialized:
            return

        self.__initialized = True
        self.sqs = boto3.resource("sqs", region_name="us-east-1")
        self.sqs.create_queue(QueueName=Queue.SCAN_PENDING)
        self.sqs.create_queue(QueueName=Queue.SCAN_RUNNING)
        self.sqs.create_queue(QueueName=Queue.SCAN_STOPPED)

        self.queue = self.sqs.get_queue_by_name(QueueName=queue)

    def enqueue(self, message):
        self.queue.send_message(MessageBody=(json.dumps(message)))

    def peek(self):
        return self.queue.receive_messages(MaxNumberOfMessages=Queue.MAX_NUMBER_OF_MESSAGES)

    def delete(self, entry):
        self.queue.delete_messages(Entries=[entry])

    def message_count(self):
        if int(os.environ["GEN_CREATE_QUEUE"]) == -1:
            client = boto3.client("sqs", region_name="us-east-1")
            response = client.get_queue_attributes(
                QueueUrl=self.queue.url,
                AttributeNames=["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"],
            )
            sqs_messages = response["Attributes"]
            message_num = sqs_messages["ApproximateNumberOfMessages"]
            message_num_not_visible = sqs_messages["ApproximateNumberOfMessagesNotVisible"]
            total_message_num = int(message_num) + int(message_num_not_visible)
            return total_message_num
        else:
            return int(os.environ["GEN_CREATE_QUEUE"])

    @staticmethod
    def dispose():
        SQSMock.__instance = None
        SQSMock.__initialized = False


class Queue(object):
    SCAN_PENDING = "ScanPending"
    SCAN_RUNNING = "ScanRunning"
    SCAN_STOPPED = "ScanStopped"

    MAX_NUMBER_OF_MESSAGES = 10

    def __init__(self, queue):
        self.queue_name = queue
        self.sqsmock = SQSMock(self.queue_name)

    def enqueue(self, message):
        self.sqsmock = SQSMock(self.queue_name)
        self.sqsmock.enqueue(message)

    def peek(self):
        self.sqsmock = SQSMock(self.queue_name)
        return self.sqsmock.peek()

    def delete(self, entry):
        self.sqsmock = SQSMock(self.queue_name)
        return self.sqsmock.delete(entry)

    def message_count(self):
        self.sqsmock = SQSMock(self.queue_name)
        return self.sqsmock.message_count()
