import boto3


class Storage(object):
    def __init__(self, bucket):
        self.s3 = boto3.resource("s3")
        self.bucket = bucket

    def load(self, key):
        obj = self.s3.Object(self.bucket, key).get()
        body = obj["Body"].read()
        return body.decode("utf-8")

    def store(self, key, body):
        obj = self.s3.Object(self.bucket, key)
        obj.put(Body=str(body).encode("utf-8"), ContentEncoding="utf-8")
        return True
