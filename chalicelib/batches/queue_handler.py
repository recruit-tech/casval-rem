from chalicelib.apis.base import APIBase
from chalicelib.core import Queue
from chalicelib.core import Scanner
from chalicelib.core.models import db
from chalicelib.core.models import Result
from chalicelib.core.models import Scan
from chalicelib.core.models import Vuln
from chalicelib.core.report import Report
from datetime import datetime
from datetime import timedelta
from peewee import fn

import json
import os
import pytz


class QueueHandler(object):
    def __init__(self, app):
        self.app = app
        jst = pytz.timezone("Asia/Tokyo")
        self.now = datetime.now(tz=pytz.utc).astimezone(jst)

    def process_scan_pending_queue(self):
        pending_queue = Queue(Queue.SCAN_PENDING)
        return self.__process_all_messages(pending_queue, self.__launch_scan)

    def process_scan_running_queue(self):
        running_queue = Queue(Queue.SCAN_RUNNING)
        return self.__process_all_messages(running_queue, self.__check_progress)

    def process_scan_stopped_queue(self):
        stopped_queue = Queue(Queue.SCAN_STOPPED)
        return self.__process_all_messages(stopped_queue, self.__notify_result)

    def __exception_handler(func):
        def self_wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self.app.log.error(e)
                raise Exception(e)

        return self_wrapper

    @__exception_handler
    def __process_all_messages(self, queue, func):
        while True:
            messages = queue.peek()
            self.app.log.debug("Messages obtained: " + str(len(messages)))

            if len(messages) is 0:
                return True

            for message in messages:
                entry = {"Id": message.message_id, "ReceiptHandle": message.receipt_handle}
                body = json.loads(message.body)
                result = func(queue, entry, body)
                if result is False:
                    return False

    def __launch_scan(self, pending_queue, entry, body):
        start_at = self.__get_datetime_in_utc(body["start_at"])
        end_at = self.__get_datetime_in_utc(body["end_at"])

        if end_at < (self.now + timedelta(hours=1)):
            self.app.log.debug("Scan abandoned: schedule_uuid=" + body["schedule_uuid"])
            body["error"] = "Scan has been abandoned because 'end_at' is soon or over."
            stopped_queue = Queue(Queue.SCAN_STOPPED)
            stopped_queue.enqueue(body)
            pending_queue.delete(entry)
            return True

        if start_at > self.now:
            # The time to scan hasn't come yet, check next message.
            return True

        running_queue = Queue(Queue.SCAN_RUNNING)
        num_of_running_scan = running_queue.message_count()
        max_scan_parallel_size = int(os.getenv("MAX_PARALLEL_SCAN_SESSION"))
        if num_of_running_scan >= max_scan_parallel_size:
            # Abandon subsequent process because other scan sessions are running.
            if num_of_running_scan > max_scan_parallel_size:
                self.app.log.error("Running scan: " + str(num_of_running_scan))
            self.app.log.debug(
                "Polling finished because number of running scan is " + str(num_of_running_scan)
            )
            return False

        if self.__is_scan_schedule_active(body["schedule_uuid"]) is False:
            # Remove the message silently because the scan session has been cancelled by user.
            self.app.log.debug(
                "Scan removed: scan has been cancelled: schedule_uuid=" + body["schedule_uuid"]
            )
            pending_queue.delete(entry)
            return True

        self.app.log.debug("Scan launched: schedule_uuid=" + body["schedule_uuid"])
        scanner = Scanner(os.getenv("SCANNER"))
        session = scanner.launch(body["target"])
        body["session"] = session
        running_queue.enqueue(body)
        pending_queue.delete(entry)
        # Do not continue subsequent process when new scan has been launched
        # because SQS sometimes returns wrong `num_of_running_scan` shortly after enqueueing
        # and that leads the handler to make a mistake on checking of parallel scaning sessions.
        return False

    def __check_progress(self, running_queue, entry, body):
        scanner = Scanner(os.environ["SCANNER"])
        stopped_queue = Queue(Queue.SCAN_STOPPED)
        if self.__is_scan_schedule_active(body["schedule_uuid"]) is False:
            # Force terminate the scan because scan session has been cancelled by user.
            self.app.log.debug("Scan terminated by user cancellation: schedule_uuid=" + body["schedule_uuid"])
            scanner.terminate(body["session"])
            running_queue.delete(entry)
            return True

        end_at = self.__get_datetime_in_utc(body["end_at"])
        if end_at <= self.now:
            self.app.log.debug("Scan terminated by timeout: schedule_uuid=" + body["schedule_uuid"])
            scanner.terminate(body["session"])
            body["error"] = "Scan has been terminated because 'end_at' is over."
            stopped_queue.enqueue(body)
            running_queue.delete(entry)
            return True

        status = scanner.check_status(body["session"])
        self.app.log.info("Scan status: {status}".format(status=status))
        if status == "complete":
            stopped_queue.enqueue(body)
            running_queue.delete(entry)
        elif status == "failure":
            body["error"] = "Scan session has been failed."
            stopped_queue.enqueue(body)
            running_queue.delete(entry)
        else:
            # Do not remove the queue entry because scan session is still running.
            self.app.log.info("Running: {schedule_uuid}".format(schedule_uuid=body["schedule_uuid"]))
        return True

    def __notify_result(self, stopped_queue, entry, body):
        scanner = Scanner(os.environ["SCANNER"])
        if "error" in body:
            self.__set_scan_error(body["schedule_uuid"], body["error"])
            stopped_queue.delete(entry)
        else:
            report_obj = Report(body["audit_id"], body["scan_id"])

            report, exception_info = report_obj.load()
            if report is None:
                self.app.log.debug(exception_info)
                self.app.log.debug("Report not found. Retrieve from scanner")
                report = scanner.get_report(body["session"])
                self.app.log.debug("Report retrieved: {} bytes".format(len(report)))
                report_obj = Report(body["audit_id"], body["scan_id"])
                report_obj.store(report)

            self.app.log.debug("Parse report")
            parse_report = scanner.parse_report(report)

            with db.atomic():
                self.__set_scan_complete(body["schedule_uuid"])
                self.__delete_scan_results(body["scan_id"])
                self.__set_scan_result(body["scan_id"], parse_report)

            stopped_queue.delete(entry)

    def __delete_scan_results(self, scan_id):
        Result.delete().where(Result.scan_id == scan_id).execute()

    def __set_scan_result(self, scan_id, report):
        # this use unit test only.
        if os.getenv("DB_TYPE") == "sqlite":
            for vuln in report["vulns"]:
                Vuln.insert(vuln).on_conflict(
                    preserve=[Vuln.fix_required], update=vuln, conflict_target=[Vuln.oid]
                ).execute()
        else:
            for vuln in report["vulns"]:
                query = Vuln.insert(vuln).on_conflict(preserve=[Vuln.fix_required], update=vuln)
                query.execute()

        for result in report["results"]:
            result["scan_id"] = scan_id
            query = Result.insert(result)
            query.execute()

    def __set_scan_error(self, schedule_uuid, error):
        scan = {"error_reason": error, "schedule_uuid": None, "scheduled": False, "processed": True}
        query = Scan.update(scan).where(Scan.schedule_uuid == schedule_uuid)
        query.execute()

    def __set_scan_complete(self, schedule_uuid):
        scan = {"error_reason": "", "schedule_uuid": None, "scheduled": False, "processed": True}
        query = Scan.update(scan).where(Scan.schedule_uuid == schedule_uuid)
        query.execute()

    def __is_scan_schedule_active(self, schedule_uuid):
        query = (
            Scan().select(fn.Count(Scan.id).alias("scan_count")).where((Scan.schedule_uuid == schedule_uuid))
        )
        scan_count = query.dicts().get()["scan_count"]
        return scan_count > 0

    def __get_datetime_in_utc(self, time_string):
        dt = datetime.strptime(time_string, APIBase.DATETIME_FORMAT)
        return dt.replace(tzinfo=pytz.utc)
