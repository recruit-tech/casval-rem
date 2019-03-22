import boto3


class S3Mock(object):

    __instance = None

    def __new__(cls, bucket):
        if cls.__instance is None:
            cls.__instance = super(S3Mock, cls).__new__(cls)
            cls.__instance.__initialized = False

        return cls.__instance

    def __init__(self, bucket):
        if self.__initialized:
            return

        self.__initialized = True
        self.s3 = boto3.resource("s3", region_name="us-east-1")
        self.bucket = bucket

        s3client = boto3.client("s3", region_name="us-east-1")
        s3client.create_bucket(Bucket=self.bucket)

    def load(self, key):
        obj = self.s3.Object(self.bucket, key).get()
        body = obj["Body"].read()
        return body.decode("utf-8")

    def store(self, key, body):
        obj = self.s3.Object(self.bucket, key)
        obj.put(Body=body.encode("utf-8"), ContentEncoding="utf-8")
        return True

    @staticmethod
    def dispose():
        S3Mock.__instance = None
        S3Mock.__initialized = False


class Storage(object):
    def __init__(self, bucket):
        self.bucket = bucket
        self.s3mock = S3Mock(self.bucket)

    def load(self, key):
        self.s3mock = S3Mock(self.bucket)
        return self.s3mock.load(key)

    def store(self, key, body):
        self.s3mock = S3Mock(self.bucket)
        return self.s3mock.store(key, body)
