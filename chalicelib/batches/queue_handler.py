import json
import os
from datetime import datetime, timedelta

import pytz
from peewee import fn

from chalicelib.apis.base import APIBase
from chalicelib.core.models import Scan
from chalicelib.core.queues import Queue
from chalicelib.core.scanner import Scanner


class QueueHandler:
    def __init__(self, app):
        self.app = app

    def __disable_if_submitted(func):
        def disable_if_submitted_wrapper(self, *args, **kwargs):
            if self.audit["submitted"] is True:
                raise Exception("audit-submitted")
            else:
                return func(self, *args, **kwargs)

    def __exception_handler(func):
        def self_wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self.app.log.error(e)
                raise Exception(e)

        return self_wrapper

    @__exception_handler
    def process_scan_pending_queue(self):
        pending_queue = Queue(Queue.SCAN_PENDING)
        running_queue = Queue(Queue.SCAN_RUNNING)
        stopped_queue = Queue(Queue.SCAN_STOPPED)

        jst = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tz=pytz.utc).astimezone(jst)

        # Check all messages in the pending queue
        while 1:
            messages = pending_queue.peek()
            self.app.log.debug("Messages obtained: " + str(len(messages)))

            if len(messages) is 0:
                break

            for message in messages:
                entry = {"Id": message.message_id, "ReceiptHandle": message.receipt_handle}

                body = json.loads(message.body)
                start_at = self.__get_datetime_in_utc(body["start_at"])
                end_at = self.__get_datetime_in_utc(body["end_at"])

                if end_at < (now + timedelta(hours=1)):
                    body["error"] = "Scan has been abandoned because 'end_at' is soon or over."
                    stopped_queue.enqueue(body)
                    pending_queue.delete(entry)
                    continue
                    raise Exception()

                if start_at > now:
                    # The time to scan hasn't come yet, check next message.
                    continue

                if running_queue.message_count() >= int(os.getenv("MAX_PARALLEL_SCAN_SESSION")):
                    # Abandon subsequent processes because other scan sessions are running.
                    break

                if self.__is_scan_schedule_active(body["schedule_uuid"]) is False:
                    # Remove the message silently because the scan session has been cancelled by user.
                    pending_queue.delete(entry)
                    continue

                self.app.log.debug("Messages processed: " + message.message_id)
                scanner = Scanner(os.getenv("SCANNER"))
                session = scanner.launch(body["target"])
                body["session"] = session
                running_queue.enqueue(body)
                pending_queue.delete(entry)

        return True

    def __is_scan_schedule_active(self, schedule_uuid):
        query = (
            Scan().select(fn.Count(Scan.id).alias("scan_count")).where((Scan.schedule_uuid == schedule_uuid))
        )
        scan_count = query.dicts().get()["scan_count"]
        return scan_count > 0

    def __get_datetime_in_utc(self, time_string):
        dt = datetime.strptime(time_string, APIBase.DATETIME_FORMAT)
        return dt.replace(tzinfo=pytz.utc)
