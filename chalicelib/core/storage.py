import boto3

REPORT_KEY_NAME = "report/{audit_id}/{scan_id}"


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
        obj.put(Body=body.encode("utf-8"), ContentEncoding="utf-8")
        return True

    def get_report_key(self, audit_id, scan_id):
        return REPORT_KEY_NAME.format(audit_id=audit_id, scan_id=scan_id)
