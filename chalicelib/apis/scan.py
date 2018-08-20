import uuid

from peewee import fn

from chalicelib.apis.base import APIBase
from chalicelib.core.models import Scan
from chalicelib.core.queues import Queue
from chalicelib.core.validators import ScanValidator


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
        body = super()._get_request_body()
        if "target" not in body or len(body["target"]) is 0:
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
        body = super()._get_request_body()
        scan = self.__get_scan_by_uuid(scan_uuid, raw=True)

        if scan["scheduled"] is True:
            raise Exception("scan-scheduled")

        if "schedule" not in body:
            raise Exception("'schedule': Must be contained.")
        if "start_at" not in body["schedule"]:
            raise Exception("'start_at': Must be contained.")
        if "end_at" not in body["schedule"]:
            raise Exception("'end_at': Must be contained.")

        start_at = body["schedule"]["start_at"]
        end_at = body["schedule"]["end_at"]

        if ScanValidator.is_valid_time_range(start_at, end_at) is False:
            raise Exception("'start_at' or 'end_at' is invalid.")

        schedule_uuid = self.__get_schedule_uuid()
        schedule = {"start_at": start_at, "end_at": end_at, "scheduled": True, "schedule_uuid": schedule_uuid}

        scan_validator = ScanValidator()
        scan_validator.validate(schedule, only=schedule)
        if scan_validator.errors:
            raise Exception(scan_validator.errors)

        self.__request_scan(
            target=scan["target"],
            start_at=start_at,
            end_at=end_at,
            schedule_uuid=schedule_uuid,
            scan_uuid=scan_uuid,
        )

        Scan.update(scan_validator.data).where(Scan.id == scan["id"]).execute()

        return self.__get_scan_by_uuid(scan_uuid)

    @APIBase.exception_handler
    @__disable_if_submitted
    def schedule_cancel(self, scan_uuid):
        scan = self.__get_scan_by_uuid(scan_uuid, raw=True)

        if scan["scheduled"] is False:
            raise Exception("scan-not-scheduled")

        unschedule = {"start_at": 0, "end_at": 0, "schedule_uuid": None, "scheduled": False}

        scan_validator = ScanValidator()
        scan_validator.validate(unschedule, only=unschedule)
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
            response["results"] = []  # TODO: Include scan results
            response["error_reason"] = scan["error_reason"]
            response["platform"] = scan["platform"]
            response["comment"] = scan["comment"]
            # TODO: Return s3.generate_presigned_url
            response["report_url"] = scan["report_url"]
            response["created_at"] = scan["created_at"].strftime(APIBase.DATETIME_FORMAT)
            response["updated_at"] = scan["updated_at"].strftime(APIBase.DATETIME_FORMAT)

            start_at = scan["start_at"]
            if type(start_at) is not str:
                start_at = start_at.strftime(APIBase.DATETIME_FORMAT)
            end_at = scan["end_at"]
            if type(end_at) is not str:
                end_at = end_at.strftime(APIBase.DATETIME_FORMAT)
            response["schedule"] = {"start_at": start_at, "end_at": end_at}

            return response

    def __get_schedule_uuid(self):
        return uuid.uuid4().hex

    def __request_scan(self, target, start_at, end_at, schedule_uuid, scan_uuid):
        queue = Queue(Queue.SCAN_PENDING)
        message = {
            "target": target,
            "start_at": start_at,
            "end_at": end_at,
            "schedule_uuid": schedule_uuid,
            "scan_uuid": scan_uuid,
        }
        queue.enqueue(message)
