import json
from datetime import datetime

import boto3
import pytz
from chalice import UnprocessableEntityError
from peewee import fn

from chalicelib.apis.base import APIBase
from chalicelib.core.models import Scan
from chalicelib.core.validators import ScanValidator

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQS_SCAN_WAITING = "ScanWaiting"


class ScanAPI(APIBase):

    @APIBase.exception_handler
    def __init__(self, app, audit_uuid):
        super().__init__(app)
        self.audit = super()._get_audit_by_uuid(audit_uuid, raw=True)


    def __disable_if_submitted(func):
        def disable_if_submitted_wrapper(self, *args, **kwargs):
            if self.audit["submitted"] is True:
                raise Exception("audit-submitted")
            else:
                return func(self, *args, **kwargs)

        return disable_if_submitted_wrapper


    @APIBase.exception_handler
    def get(self, scan_uuid):
        return self.__get_scan_by_uuid(scan_uuid)

    @APIBase.exception_handler
    @__disable_if_submitted
    def post(self):
        if self.audit["submitted"] is True:
            raise Exception("audit-submitted")

        body = super()._get_request_body()
        if "target" not in body:
            raise Exception("target-is-empty")

        scan_validator = ScanValidator()
        scan_validator.validate({"target": body["target"]}, only=("target"))
        if scan_validator.errors:
            raise Exception(scan_validator.errors)
        target = scan_validator.data["target"]

        scan_query = (
            Scan()
            .select(fn.Count(Scan.id).alias("scan_count"))
            .where((Scan.audit_id == self.audit["id"]) & (Scan.target == target) & (Scan.scheduled is True))
        )
        scan_count = scan_query.dicts().get()["scan_count"]
        if scan_count > 0:
            raise Exception("target-is-scheduled")

        scan = Scan(target=target, audit_id=self.audit["id"], platform=self.__get_platform(target))
        scan.save()

        return self.__get_scan_by_uuid(scan.uuid)

    @APIBase.exception_handler
    @__disable_if_submitted
    def patch(self, scan_uuid):
        body = super()._get_request_body()
        scan = self.__get_scan_by_uuid(scan_uuid, raw=True)

        if "comment" not in body:
            raise Exception("'comment': Must be contained.")
        key_filter = "comment"
        scan_new = {k: v for k, v in body.items() if k in key_filter}
        if scan_new:
            scan_validator = ScanValidator()
            scan_validator.validate(scan_new, only=scan_new)
            if scan_validator.errors:
                raise Exception(scan_validator.errors)
            Scan.update(scan_validator.data).where(Scan.id == scan["id"]).execute()

        return self.__get_scan_by_uuid(scan_uuid)

    @APIBase.exception_handler
    @__disable_if_submitted
    def delete(self, scan_uuid):
        query = Scan.delete().where(Scan.uuid == scan_uuid)
        row_count = query.execute()
        if row_count == 0:
            raise IndexError("'scan_uuid': Item could not be found.")
        return {}

    @APIBase.exception_handler
    @__disable_if_submitted
    def schedule(self, scan_uuid):
        body = self.app.current_request.json_body

        if "schedule" not in body:
            raise Exception("Request has no key `schedule`")
        if "start_at" not in body["schedule"]:
            raise Exception("Request has no key `start_at`")
        if "end_at" not in body["schedule"]:
            raise Exception("Request has no key `end_at`")

        try:
            start_at = datetime.strptime(body["schedule"]["start_at"], DATETIME_FORMAT)
            start_at = start_at.replace(tzinfo=pytz.utc)
            end_at = datetime.strptime(body["schedule"]["end_at"], DATETIME_FORMAT)
            end_at = end_at.replace(tzinfo=pytz.utc)
            jst = pytz.timezone("Asia/Tokyo")
            now = datetime.now(tz=pytz.utc).astimezone(jst)
        except Exception as e:
            raise Exception(e)

        if end_at <= start_at:
            raise Exception("`end_at` in the request is equal or earlier than `start_at`")
        if start_at <= now:
            raise Exception("`start_at` in the request has elapsed")
        if end_at <= now:
            raise Exception("`end_at` in the request has elapsed")

        # ToDo: store schedule to Aurora Serverless
        # Add schedule uuid

        try:
            message = {
                "target": "csrf.jp",
                "start_at": body["schedule"]["start_at"],
                "end_at": body["schedule"]["end_at"],
                "scan_uuid": scan_uuid,
            }
            sqs = boto3.resource("sqs")
            queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_WAITING)
            queue.send_message(MessageBody=(json.dumps(message)))
        except Exception as e:
            raise UnprocessableEntityError(e)  # consider to use decorator

        response = {
            "target": "127.0.0.1",
            "audit": {"id": "3cd708cefd58401f9d43ff953f063467"},
            "id": "21d6cd7b33e84fbf9a2898f4ea7f90cc",
            "status": {"scheduled": False, "processed": False},
            "schedule": {"start_at": "2017-12-27 21:00:00", "end_at": "2017-12-27 22:00:00"},
            "results": [
                {
                    "id": "8b3d704e-5649-4794-8a78-54eec555e44e",
                    "oid": "1.3.6.1.4.1.25623.1.0.105879",
                    "protocol": "tcp",
                    "port": 443,
                    "name": "SSL/TLS: HTTP Strict Transport Security (HSTS) Missing",
                    "threat": "Log",
                    "fix_required": False,
                }
            ],
            "error_reason": "指定されたホストが見つかりませんでした",
            "platform": "aws",
            "comment": "誤検知なので修正不要と判断した",
            "report_url": "https://s3/pre-signed-url",
            "created_at": "2018-10-10 23:59:59",
            "updated_at": "2018-10-10 23:59:59",
        }
        return response

    @APIBase.exception_handler
    @__disable_if_submitted
    def schedule_cancel(self, scan_uuid):
        body = super()._get_request_body()
        scan = self.__get_scan_by_uuid(scan_uuid, raw=True)

        if scan["scheduled"] is False:
            raise Exception("scan-not-scheduled")

        unscheduled = {
            "start_at": 0,
            "end_at": 0,
            "schedule_uuid": None,
            "scheduled": False
        }

        scan_validator = ScanValidator()
        scan_validator.validate(unscheduled, only=unscheduled)
        if scan_validator.errors:
            raise Exception(scan_validator.errors)

        Scan.update(scan_validator.data).where(Scan.id == scan["id"]).execute()

        return self.__get_scan_by_uuid(scan_uuid)


    def __get_platform(self, target):
        if ScanValidator.is_AWS(target) is True:
            return "aws"
        else:
            return "unknown"

    def __get_scan_by_uuid(self, uuid, raw=False):
        scans = Scan.select().where(Scan.uuid == uuid)
        scan = scans.dicts()[0]

        if raw is True:
            return scan

        else:
            response = {}
            response["target"] = scan["target"]
            response["uuid"] = scan["uuid"].hex
            response["status"] = {"scheduled": scan["scheduled"], "processed": scan["processed"]}
            response["schedule"] = {"start_at": scan["start_at"], "end_at": scan["end_at"]}
            response["results"] = []  # TODO: Include scan results
            response["error_reason"] = scan["error_reason"]
            response["platform"] = scan["platform"]
            response["comment"] = scan["comment"]
            # TODO: Return s3.generate_presigned_url
            response["report_url"] = scan["report_url"]
            # TODO: Change to UTC
            response["created_at"] = scan["created_at"].strftime(APIBase.RESPONSE_TIME_FORMAT)
            # TODO: Change to UTC
            response["updated_at"] = scan["updated_at"].strftime(APIBase.RESPONSE_TIME_FORMAT)

            return response
