import boto3
import json
import pytz

from datetime import datetime
from chalice import BadRequestError
from chalice import UnprocessableEntityError

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQS_SCAN_WAITING = "ScanWaiting"


def get(scan_id):
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


def post():
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


def patch(app, scan_id):
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


def delete(scan_id):
    return {}


def schedule(app, scan_id):
    # Chalice raises an exception internally if a request is an invalid JSON
    body = app.current_request.json_body

    if "schedule" not in body:
        raise BadRequestError("Request has no key `schedule`")
    if "start_at" not in body["schedule"]:
        raise BadRequestError("Request has no key `start_at`")
    if "end_at" not in body["schedule"]:
        raise BadRequestError("Request has no key `end_at`")

    try:
        start_at = datetime.strptime(body["schedule"]["start_at"], DATETIME_FORMAT)
        start_at = start_at.replace(tzinfo=pytz.utc)
        end_at = datetime.strptime(body["schedule"]["end_at"], DATETIME_FORMAT)
        end_at = end_at.replace(tzinfo=pytz.utc)
        jst = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tz=pytz.utc).astimezone(jst)
    except Exception as e:
        raise BadRequestError(e)

    if end_at <= start_at:
        raise BadRequestError("`end_at` in the request is equal or earlier than `start_at`")
    if end_at <= now:
        raise BadRequestError("`end_at` in the request has elapsed")

    # ToDo: store schedule to DynamoDB

    try:
        message = {
            "target": "127.0.0.1",
            "start_at": body["schedule"]["start_at"],
            "end_at": body["schedule"]["end_at"],
            "scan_id": scan_id,
        }
        sqs = boto3.resource("sqs")
        queue = sqs.get_queue_by_name(QueueName=SQS_SCAN_WAITING)
        result = queue.send_message(MessageBody=(json.dumps(message)))
    except Exception as e:
        raise UnprocessableEntityError(e)

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


def schedule_cancel(scan_id):
    return {}
