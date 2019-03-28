# fmt: off
import os
from tests.load_env import loadenv  # noqa: F402
loadenv("local")   # noqa: F402
os.environ["DB_TYPE"] = "sqlite"   # noqa: F402
os.environ["UNIT_TEST"] = "True"   # noqa: F402
# fmt: on

from app import app
from chalicelib.apis import ScanAPI
from chalicelib.batches.queue_handler import QueueHandler
from chalicelib.core import Queue
from chalicelib.core.models import db
from chalicelib.core.stub.queues import SQSMock
from moto import mock_sqs
from peewee_seed import PeeweeSeed

import freezegun
import json


path_carrent = os.path.abspath(".")


def session_factory():
    entry = {
        "Id": "5fea7756-0ea4-451a-a703-a558b933e274",
        "ReceiptHandle": "MbZj6wDWli+JvwwJaBV+3dcjk2YW2vA3+STFFljTM8tJJg6HRG6PYSasuWXPJB+Cw"
        "Lj1FjgXUv1uSj1gUPAWV66FU/WeR4mq2OKpEGYWbnLmpRCJVAyeMjeU5ZBdtcQ+QE"
        "auMZc8ZRv37sIW2iJKq3M9MFx1YvV11A2x/KSbkJ0=",
    }
    body = {
        "target": "127.0.0.1",
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
        seeds.drop_table_all(fixtures_list, foreign_key_checks=True)
    else:
        seeds.create_table_all()
        seeds.db_data_input()


class TestQueueHandler(object):
    def setup_class(self):
        db_seed()
        os.environ["GEN_CREATE_QUEUE"] = str(0)

    def teardown_method(self):
        SQSMock.dispose()
        os.environ["GEN_CREATE_QUEUE"] = str(0)

    # the normal handler
    # ex :
    # freeze_time('2018-12-26 08:00:00+00:00') は実際にはこれがutcになるので
    # jstでは`2018-12-26 17:00:00+09:00`となる

    # check queue message in pod ip address
    @mock_sqs
    @freezegun.freeze_time("2018-12-27 10:00:00")
    def test_deploy_scanapi(self):
        pending_queue = Queue(Queue.SCAN_PENDING)
        running_queue = Queue(Queue.SCAN_RUNNING)

        scanapi = ScanAPI(app, "3cd708cefd58401f9d43ff953f063467")

        os.environ["DEPLOY_SERVICE_MOCE_IP"] = "10.0.0.10"
        entry, body = session_factory()

        scanapi._ScanAPI__request_scan(
            target="127.0.0.1",
            start_at=body["start_at"],
            end_at=body["end_at"],
            schedule_uuid=scanapi._ScanAPI__get_schedule_uuid(),
            scan_id="21d6cd7b33e84fbf9a2898f4ea7f90ca",
            audit_id="3cd708cefd58401f9d43ff953f063467",
        )
        pending_messages = pending_queue.peek()
        body = {}

        for message in pending_messages:
            entry = {"Id": message.message_id, "ReceiptHandle": message.receipt_handle}
            body = json.loads(message.body)

        assert body["req_ip"] == "10.0.0.10"

        handler = QueueHandler(app)
        assert handler._QueueHandler__launch_scan(pending_queue, entry, body)

        running_messages = running_queue.peek()

        for message in running_messages:
            body = json.loads(message.body)

        assert body["req_ip"] == "10.0.0.10"
