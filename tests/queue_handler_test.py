# fmt: off
from tests.load_env import loadenv  # noqa: F402
import os
loadenv("local")   # noqa: F402
os.environ["DB_TYPE"] = "sqlite"   # noqa: F402
os.environ["UNIT_TEST"] = "True"   # noqa: F402
# fmt: on

from app import app
from chalicelib.batches.queue_handler import QueueHandler
from chalicelib.core import Queue
from chalicelib.core.models import db
from chalicelib.core.models import Scan
from chalicelib.core.report import Report
from chalicelib.core.stub.queues import SQSMock
from chalicelib.core.stub.storage import S3Mock
from moto import mock_s3
from moto import mock_sqs
from peewee_seed import PeeweeSeed

import freezegun


path_carrent = os.path.abspath(".")


def session_factory():
    entry = {
        "Id": "5fea7756-0ea4-451a-a703-a558b933e274",
        "ReceiptHandle": "MbZj6wDWli+JvwwJaBV+3dcjk2YW2vA3+STFFljTM8tJJg6HRG6PYSasuWXPJB+Cw"
        "Lj1FjgXUv1uSj1gUPAWV66FU/WeR4mq2OKpEGYWbnLmpRCJVAyeMjeU5ZBdtcQ+QE"
        "auMZc8ZRv37sIW2iJKq3M9MFx1YvV11A2x/KSbkJ0=",
    }
    body = {
        "target": "csrf.jp",
        "start_at": "2018-12-27 09:00:00",
        "end_at": "2018-12-27 14:00:00",
        "schedule_uuid": "e3a398ca0bb74673b582c4c81d6c2f03",
        "scan_id": 4,
        "audit_id": 4,
        "session": {"host": "127.0.0.1", "target_id": "<scan_id>", "port": 9390, "scan_id": "<target_id>"},
    }
    return entry, body


def db_seed(remove=False):
    path = path_carrent + "/chalicelib/apis/fixtures/"
    fixtures_list = ["audits.json", "scans.json", "contacts.json", "results.json", "vulns.json"]
    seeds = PeeweeSeed(db, path, fixtures_list)
    if remove:
        # bugfix to Library
        seeds.drop_table_all(fixtures_list, foreign_key_checks=True)
    else:
        seeds.create_table_all()
        seeds.db_data_input()


class TestQueueHandler(object):
    def setup_class(self):
        # db_seed()
        os.environ["GEN_CREATE_QUEUE"] = str(0)

    def teardown_method(self):
        SQSMock.dispose()
        S3Mock.dispose()
        os.environ["GEN_CREATE_QUEUE"] = str(0)

    # the normal handler
    # ex :
    # freeze_time('2018-12-26 08:00:00+00:00') は実際にはこれがutcになるので
    # jstでは`2018-12-26 17:00:00+09:00`となる

    # pending queue
    @mock_sqs
    @freezegun.freeze_time("2018-12-27 15:00:00")
    def test_launch_scan_over_time(self):
        pending_queue = Queue(Queue.SCAN_PENDING)
        handler = QueueHandler(app)
        entry, body = session_factory()

        assert handler._QueueHandler__launch_scan(pending_queue, entry, body)

    @mock_sqs
    @freezegun.freeze_time("2018-12-26 08:00:00")
    def test_launch_scan_early_time(self):
        pending_queue = Queue(Queue.SCAN_PENDING)
        handler = QueueHandler(app)
        entry, body = session_factory()

        assert handler._QueueHandler__launch_scan(pending_queue, entry, body)

    @mock_sqs
    @freezegun.freeze_time("2018-12-27 10:00:00")
    def test_launch_scan_parallel_size_over(self):
        pending_queue = Queue(Queue.SCAN_PENDING)
        running_queue = Queue(Queue.SCAN_RUNNING)

        handler = QueueHandler(app)
        entry, body = session_factory()
        # os.environ["GEN_CREATE_QUEUE"] = str(10)
        os.environ["GEN_CREATE_QUEUE"] = str(-1)
        print(id(pending_queue))
        for i in range(11):
            entry["Id"] = entry["Id"][: len(entry["Id"])] + str(i)
            entry["ReceiptHandle"] = entry["ReceiptHandle"][: len(entry["ReceiptHandle"])] + str(i)

            running_queue.enqueue(entry)

        assert not handler._QueueHandler__launch_scan(pending_queue, entry, body)

    @mock_sqs
    @freezegun.freeze_time("2018-12-27 10:00:00")
    def test_launch_scan_is_not_active(self):
        pending_queue = Queue(Queue.SCAN_PENDING)
        handler = QueueHandler(app)
        entry, body = session_factory()

        assert handler._QueueHandler__launch_scan(pending_queue, entry, body)

    @mock_sqs
    @freezegun.freeze_time("2018-12-27 10:00:00")
    def test_launch_scan_otherwise(self):
        pending_queue = Queue(Queue.SCAN_PENDING)
        handler = QueueHandler(app)
        entry, body = session_factory()
        pending_queue.enqueue(body)
        schedule_id = Scan.get((Scan.id == 1))
        schedule_id.schedule_uuid = body["schedule_uuid"]
        schedule_id.save()

        assert not handler._QueueHandler__launch_scan(pending_queue, entry, body)

    # running queue
    @mock_sqs
    def test_check_progress_is_not_active(self):
        running_queue = Queue(Queue.SCAN_RUNNING)
        handler = QueueHandler(app)
        entry, body = session_factory()
        schedule_id = Scan.get((Scan.id == 1))
        schedule_id.schedule_uuid = None
        schedule_id.save()
        assert handler._QueueHandler__check_progress(running_queue, entry, body)

    @mock_sqs
    @freezegun.freeze_time("2018-12-27 15:00:00")
    def test_check_progress_over_time(self):
        running_queue = Queue(Queue.SCAN_RUNNING)
        handler = QueueHandler(app)
        entry, body = session_factory()
        schedule_id = Scan.get((Scan.id == 1))
        schedule_id.schedule_uuid = body["schedule_uuid"]
        schedule_id.save()
        assert handler._QueueHandler__check_progress(running_queue, entry, body)

    @mock_sqs
    @freezegun.freeze_time("2018-12-27 10:00:00")
    def test_check_progress_otherwise(self):
        running_queue = Queue(Queue.SCAN_RUNNING)
        handler = QueueHandler(app)
        entry, body = session_factory()
        assert handler._QueueHandler__check_progress(running_queue, entry, body)

    # stopped queue
    @mock_sqs
    def test_notify_result_body_in_error(self):

        stopped_queue = Queue(Queue.SCAN_STOPPED)
        handler = QueueHandler(app)
        entry, body = session_factory()

        stopped_queue.enqueue(entry)
        body["error"] = "error_reason_why"
        os.environ["GEN_CREATE_QUEUE"] = str(-1)
        message = stopped_queue.peek()[0]
        entry = {"Id": message.message_id, "ReceiptHandle": message.receipt_handle}

        handler._QueueHandler__notify_result(stopped_queue, entry, body)

        assert 0 == stopped_queue.message_count()

    @mock_sqs
    @mock_s3
    def test_notify_result_no_get_report(self):

        stopped_queue = Queue(Queue.SCAN_STOPPED)
        handler = QueueHandler(app)
        entry, body = session_factory()

        stopped_queue.enqueue(entry)
        os.environ["GEN_CREATE_QUEUE"] = str(-1)
        message = stopped_queue.peek()[0]
        entry = {"Id": message.message_id, "ReceiptHandle": message.receipt_handle}
        schedule_id = Scan.get((Scan.id == 1))
        schedule_id.schedule_uuid = body["schedule_uuid"]
        schedule_id.save()

        handler._QueueHandler__notify_result(stopped_queue, entry, body)

        assert 0 == stopped_queue.message_count()

        report_obj = Report(body["audit_id"], body["scan_id"])
        assert report_obj.load()[0] == '<report content_type="text/xml"></report>'

    @mock_sqs
    @mock_s3
    def test_notify_result_otherwise(self):
        stopped_queue = Queue(Queue.SCAN_STOPPED)
        handler = QueueHandler(app)
        entry, body = session_factory()
        stopped_queue.enqueue(body)
        schedule_id = Scan.get((Scan.id == 1))
        schedule_id.schedule_uuid = body["schedule_uuid"]
        schedule_id.save()
        os.environ["GEN_CREATE_QUEUE"] = str(0)

        handler._QueueHandler__launch_scan(stopped_queue, entry, body)
        assert 0 == stopped_queue.message_count()
