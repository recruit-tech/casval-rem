import boto3


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


def patch(scan_id):

    sqs = boto3.client("sqs")
    r = sqs.send_message(QueueUrl=url, DelaySeconds=0, MessageBody=(json.dumps(body)))

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


def schedule(scan_id):
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
