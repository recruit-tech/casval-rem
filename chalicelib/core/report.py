from chalicelib.core.storage import Storage

import os

REPORT_KEY_NAME = "report/{audit_id}/{scan_id}"


class Report(object):
    def __init__(self, audit_id, scan_id):
        self.audit_id = audit_id
        self.scan_id = scan_id
        self.key = REPORT_KEY_NAME.format(audit_id=audit_id, scan_id=scan_id)
        self.storage = Storage(os.getenv("S3_BUCKET_NAME"))

    def load(self):
        try:
            report = self.storage.load(self.key)
            return report
        except Exception as e:
            return None, e

    def store(self, report):
        return self.storage.store(self.key, report)
