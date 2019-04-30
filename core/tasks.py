from datetime import datetime
from datetime import timedelta

import pytz
from flask import current_app as app
from peewee import fn

from core import db
from scanner import Scanner

from .models import ResultTable
from .models import ScanTable
from .models import TaskProgressValue
from .models import TaskTable
from .models import VulnTable
from .utils import Utils

SCAN_MAX_NUMBER_OF_MESSAGES_IN_QUEUE = 10
SCAN_MAX_PARALLEL_SESSION = 2
TASK_HARD_DELETE = False


class TaskUtils:
    @staticmethod
    def get_task_count(progress):
        task_query = TaskTable.select(fn.Count(TaskTable.id).alias("task_count")).where(
            TaskTable.progress == progress
        )
        return task_query.dicts().get()["task_count"]

    @staticmethod
    def get_tasks(progress):
        task_query = (
            TaskTable.select().where(TaskTable.progress == progress).order_by(TaskTable.updated_at.desc())
        )
        return list(task_query.dicts())

    @staticmethod
    def is_task_expired(task_uuid):
        scan_query = (
            ScanTable()
            .select(fn.Count(ScanTable.id).alias("scan_count"))
            .where((ScanTable.task_uuid == task_uuid))
        )
        return scan_query.dicts().get()["scan_count"] == 0

    @staticmethod
    def delete(task_uuid):
        if TASK_HARD_DELETE == True:
            TaskTable.delete().where(TaskTable.uuid == task_uuid).execute()
        else:
            TaskTable.update({"progress": TaskProgressValue.DELETED.name}).where(
                TaskTable.uuid == task_uuid
            ).execute()
        return True


class PendingTask:
    @staticmethod
    def handle():
        for task in TaskUtils.get_tasks(TaskProgressValue.PENDING.name):

            start_at = task["start_at"].replace(tzinfo=pytz.utc)
            end_at = task["end_at"].replace(tzinfo=pytz.utc)
            now = datetime.now(tz=pytz.utc).astimezone(pytz.timezone("Asia/Tokyo"))

            if start_at > now:
                # The time to scan hasn't come yet, check next task.
                continue

            if end_at < (now + timedelta(hours=1)):
                app.logger.info("Pending task: abandoned, task_uuid={}".format(task["uuid"]))
                task["error_reason"] = "Scan has been abandoned because 'end_at' is soon or over."
                task["progress"] = TaskProgressValue.FAILED.name
                TaskTable.update(task).where(TaskTable.id == task["id"]).execute()
                continue

            if TaskUtils.is_task_expired(task["uuid"]):
                app.logger.info(
                    "Pending task: {} removed, scan has been cancelled by user.".format(task["uuid"])
                )
                TaskUtils.delete(task["uuid"])
                continue

            running_task_count = TaskUtils.get_task_count(TaskProgressValue.RUNNING.name)
            if running_task_count >= SCAN_MAX_PARALLEL_SESSION:
                # Abandon subsequent process because other scan sessions are running.
                app.logger.info(
                    "Pending task: abandoned, running tasks are more than {}.".format(running_task_count)
                )
                break

            app.logger.info("Pending task: launched, task_uuid={}".format(task["uuid"]))
            Scanner.launch(body["target"])
            task["session"] = "__session__"
            task["progress"] = TaskProgressValue.RUNNING.name
            TaskTable.update(task).where(TaskTable.id == task["id"]).execute()
            # Do not continue subsequent loop when new scan has been launched
            # because each stan required much time and it is likely to reach the parallel running task limit.
            break

        return True

    @staticmethod
    def add(entry):
        task = TaskTable(**entry)
        task.save()
        return task


class RunningTask:
    @staticmethod
    def handle():
        for task in TaskUtils.get_tasks(TaskProgressValue.RUNNING.name):

            if TaskUtils.is_task_expired(task["uuid"]):
                # Force terminate the scan because scan session has been cancelled by user.
                app.logger.info(
                    "Running task: {} removed, scan has been cancelled by user.".format(task["uuid"])
                )
                Scanner.terminate(task["session"])
                TaskUtils.delete(task["uuid"])
                continue

            end_at = task["end_at"].replace(tzinfo=pytz.utc)
            now = datetime.now(tz=pytz.utc).astimezone(pytz.timezone("Asia/Tokyo"))
            if end_at <= now:
                app.logger.info("Running task: terminated by timeout, task_uuid={}".format(task["uuid"]))
                Scanner.terminate(test["session"])
                task["error_reason"] = "Scan has been terminated because 'end_at' is over."
                task["progress"] = TaskProgressValue.FAILED.name
                TaskTable.update(task).where(TaskTable.id == task["id"]).execute()
                continue

            status = Scanner.check_status(task["session"])
            if status == "complete":
                task["progress"] = TaskProgressValue.STOPPED.name
                TaskTable.update(task).where(TaskTable.id == task["id"]).execute()
            elif status == "failure":
                body["error_reason"] = "Scan session has failed."
                task["progress"] = TaskProgressValue.FAILED.name
                TaskTable.update(task).where(TaskTable.id == task["id"]).execute()
            else:
                # Do not remove the queue entry because scan session is still running.
                app.logger.info("Running task: ongoing, task_uuid={}".format(task["uuid"]))

        return True


class StoppedTask:
    @staticmethod
    def handle():
        for task in TaskUtils.get_tasks(TaskProgressValue.STOPPED.name):

            report_obj = "storage"  # Report(task["audit_id"], task["scan_id"])
            report = None
            exception_info = None

            # report, exception_info = report_obj.load()
            if report is None:
                app.logger.info(exception_info)
                app.logger.info("Report not found. Retrieve from scanner")
                report = Scanner.get_report(task["session"])
                app.logger.info("Report retrieved: {} bytes".format(len(report)))
                # report_obj = Report(task["audit_id"], task["scan_id"])
                # report_obj.store(report)

            app.logger.info("Parse report")
            report = Scanner.parse_report(report)

            with db.database.atomic():

                if TaskUtils.is_task_expired(task["uuid"]) == False:

                    data = {
                        "error_reason": "",
                        "task_uuid": None,
                        "scheduled": False,
                        "processed": True,
                        "start_at": Utils.get_default_datetime(),
                        "end_at": Utils.get_default_datetime(),
                    }

                    scan_query = ScanTable.update(data).where(ScanTable.task_uuid == task["uuid"])
                    scan_query.execute()

                    ResultTable.delete().where(ResultTable.scan_id == task["scan_id"]).execute()

                    for vuln in report["vulns"]:
                        vuln_query = VulnTable.insert(vuln).on_conflict(
                            preserve=[VulnTable.fix_required], update=vuln
                        )
                        vuln_query.execute()

                    for result in report["results"]:
                        result["scan_id"] = task["scan_id"]
                        result_query = ResultTable.insert(result)
                        result_query.execute()

                TaskUtils.delete(task["uuid"])

        return True


class FailedTask:
    @staticmethod
    def handle():
        for task in TaskUtils.get_tasks(TaskProgressValue.FAILED.name):

            data = {
                "error_reason": task["error_reason"],
                "task_uuid": None,
                "scheduled": False,
                "processed": True,
                "start_at": Utils.get_default_datetime(),
                "end_at": Utils.get_default_datetime(),
            }
            scan_query = ScanTable.update(data).where(ScanTable.task_uuid == task["uuid"])
            scan_query.execute()

            TaskUtils.delete(task["uuid"])

        return True


class DeletedTask:
    @staticmethod
    def handle():
        # TODO
        print("handle!")
        return {}
