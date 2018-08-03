import os

from chalice import Chalice
from chalice import CORSConfig

app = Chalice(app_name='casval')
app.debug = True

cors_config = CORSConfig(
    allow_origin=os.environ["ORIGIN"],
    allow_headers=['Authorization'],
    max_age=3600,
)


@app.route('/audit', methods=['GET'], cors=cors_config)
def audit_index():
    response = [
        {
            "name": "コーポレートサイト",
            "contacts": [
                {
                    "name": "nishimunea",
                    "email": "nishimunea@example.jp"
                }
            ],
            "id": "3cd708cefd58401f9d43ff953f063467",
            "scans": [
                "21d6cd7b33e84fbf9a2898f4ea7f90cc"
            ],
            "submitted": False,
            "rejected_reason": "深刻な脆弱性が修正されていません",
            "restricted_by": {
                "ip": True,
                "password": False
            },
            "created_at": "2018-10-10 23:59:59",
            "updated_at": "2018-10-10 23:59:59"
        }
    ]
    return response


@app.route('/audit', methods=['POST'], cors=cors_config)
def audit_post():
    response = {
        "name": "コーポレートサイト",
        "contacts": [
            {
                "name": "nishimunea",
                "email": "nishimunea@example.jp"
            }
        ],
        "id": "3cd708cefd58401f9d43ff953f063467",
        "scans": [
            "21d6cd7b33e84fbf9a2898f4ea7f90cc"
        ],
        "submitted": False,
        "rejected_reason": "深刻な脆弱性が修正されていません",
        "restricted_by": {
            "ip": True,
            "password": False
        },
        "created_at": "2018-10-10 23:59:59",
        "updated_at": "2018-10-10 23:59:59"
    }
    return response


@app.route('/audit/{audit_id}/tokens', methods=['POST'], cors=cors_config)
def audit_post(audit_id):
    response = {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
                 ".eyJzY29wZSI6IjNjZDcwOGNlZmQ1ODQwMWY5ZDQzZmY5NTNmMDYzNDY3IiwiZXhwIjoxNTE1MTUxNTE1fQ"
                 ".UNb9VCWBhVcJgtA1dGl-4QWcBXhfxKgaJuxqIdsBDyc"
    }
    return response


@app.route('/audit/{audit_id}', methods=['GET'], cors=cors_config)
def audit_get(audit_id):
    response = {
        "name": "コーポレートサイト",
        "contacts": [
            {
                "name": "nishimunea",
                "email": "nishimunea@example.jp"
            }
        ],
        "id": "3cd708cefd58401f9d43ff953f063467",
        "scans": [
            "21d6cd7b33e84fbf9a2898f4ea7f90cc"
        ],
        "submitted": False,
        "rejected_reason": "深刻な脆弱性が修正されていません",
        "restricted_by": {
            "ip": True,
            "password": False
        },
        "created_at": "2018-10-10 23:59:59",
        "updated_at": "2018-10-10 23:59:59"
    }
    return response


@app.route('/audit/{audit_id}', methods=['PATCH'], cors=cors_config)
def audit_patch(audit_id):
    response = {
        "name": "コーポレートサイト",
        "contacts": [
            {
                "name": "nishimunea",
                "email": "nishimunea@example.jp"
            }
        ],
        "id": "3cd708cefd58401f9d43ff953f063467",
        "scans": [
            "21d6cd7b33e84fbf9a2898f4ea7f90cc"
        ],
        "submitted": False,
        "rejected_reason": "深刻な脆弱性が修正されていません",
        "restricted_by": {
            "ip": True,
            "password": False
        },
        "created_at": "2018-10-10 23:59:59",
        "updated_at": "2018-10-10 23:59:59"
    }
    return response


@app.route('/audit/{audit_id}', methods=['DELETE'], cors=cors_config)
def audit_delete(audit_id):
    return {}


@app.route('/audit/{audit_id}/submit', methods=['POST'], cors=cors_config)
def audit_submit(audit_id):
    return {}


@app.route('/audit/{audit_id}/submit', methods=['DELETE'], cors=cors_config)
def audit_submit_cancel(audit_id):
    return {}


@app.route('/scan', methods=['POST'], cors=cors_config)
def scan_post():
    response = {
        "target": "127.0.0.1",
        "audit": {
            "id": "3cd708cefd58401f9d43ff953f063467"
        },
        "id": "21d6cd7b33e84fbf9a2898f4ea7f90cc",
        "status": {
            "scheduled": False,
            "processed": False
        },
        "schedule": {
            "start_at": "2017-12-27 21:00:00",
            "end_at": "2017-12-27 22:00:00"
        },
        "results": [
            {
                "id": "8b3d704e-5649-4794-8a78-54eec555e44e",
                "oid": "1.3.6.1.4.1.25623.1.0.105879",
                "protocol": "tcp",
                "port": 443,
                "name": "SSL/TLS: HTTP Strict Transport Security (HSTS) Missing",
                "threat": "Log",
                "fix_required": False
            }
        ],
        "error_reason": "指定されたホストが見つかりませんでした",
        "platform": "aws",
        "comment": "誤検知なので修正不要と判断した",
        "report_url": "https://s3/pre-signed-url",
        "created_at": "2018-10-10 23:59:59",
        "updated_at": "2018-10-10 23:59:59"
    }
    return response


@app.route('/scan/{scan_id}', methods=['GET'], cors=cors_config)
def scan_get(scan_id):
    response = {
        "target": "127.0.0.1",
        "audit": {
            "id": "3cd708cefd58401f9d43ff953f063467"
        },
        "id": "21d6cd7b33e84fbf9a2898f4ea7f90cc",
        "status": {
            "scheduled": False,
            "processed": False
        },
        "schedule": {
            "start_at": "2017-12-27 21:00:00",
            "end_at": "2017-12-27 22:00:00"
        },
        "results": [
            {
                "id": "8b3d704e-5649-4794-8a78-54eec555e44e",
                "oid": "1.3.6.1.4.1.25623.1.0.105879",
                "protocol": "tcp",
                "port": 443,
                "name": "SSL/TLS: HTTP Strict Transport Security (HSTS) Missing",
                "threat": "Log",
                "fix_required": False
            }
        ],
        "error_reason": "指定されたホストが見つかりませんでした",
        "platform": "aws",
        "comment": "誤検知なので修正不要と判断した",
        "report_url": "https://s3/pre-signed-url",
        "created_at": "2018-10-10 23:59:59",
        "updated_at": "2018-10-10 23:59:59"
    }
    return response


@app.route('/scan/{scan_id}', methods=['PATCH'], cors=cors_config)
def scan_patch(scan_id):
    response = {
        "target": "127.0.0.1",
        "audit": {
            "id": "3cd708cefd58401f9d43ff953f063467"
        },
        "id": "21d6cd7b33e84fbf9a2898f4ea7f90cc",
        "status": {
            "scheduled": False,
            "processed": False
        },
        "schedule": {
            "start_at": "2017-12-27 21:00:00",
            "end_at": "2017-12-27 22:00:00"
        },
        "results": [
            {
                "id": "8b3d704e-5649-4794-8a78-54eec555e44e",
                "oid": "1.3.6.1.4.1.25623.1.0.105879",
                "protocol": "tcp",
                "port": 443,
                "name": "SSL/TLS: HTTP Strict Transport Security (HSTS) Missing",
                "threat": "Log",
                "fix_required": False
            }
        ],
        "error_reason": "指定されたホストが見つかりませんでした",
        "platform": "aws",
        "comment": "誤検知なので修正不要と判断した",
        "report_url": "https://s3/pre-signed-url",
        "created_at": "2018-10-10 23:59:59",
        "updated_at": "2018-10-10 23:59:59"
    }
    return response


@app.route('/scan/{scan_id}', methods=['DELETE'], cors=cors_config)
def scan_delete(scan_id):
    return {}


@app.route('/scan/{scan_id}/schedule', methods=['PATCH'], cors=cors_config)
def scan_schedule(scan_id):
    response = {
        "target": "127.0.0.1",
        "audit": {
            "id": "3cd708cefd58401f9d43ff953f063467"
        },
        "id": "21d6cd7b33e84fbf9a2898f4ea7f90cc",
        "status": {
            "scheduled": False,
            "processed": False
        },
        "schedule": {
            "start_at": "2017-12-27 21:00:00",
            "end_at": "2017-12-27 22:00:00"
        },
        "results": [
            {
                "id": "8b3d704e-5649-4794-8a78-54eec555e44e",
                "oid": "1.3.6.1.4.1.25623.1.0.105879",
                "protocol": "tcp",
                "port": 443,
                "name": "SSL/TLS: HTTP Strict Transport Security (HSTS) Missing",
                "threat": "Log",
                "fix_required": False
            }
        ],
        "error_reason": "指定されたホストが見つかりませんでした",
        "platform": "aws",
        "comment": "誤検知なので修正不要と判断した",
        "report_url": "https://s3/pre-signed-url",
        "created_at": "2018-10-10 23:59:59",
        "updated_at": "2018-10-10 23:59:59"
    }
    return response


@app.route('/scan/{scan_id}/schedule', methods=['DELETE'], cors=cors_config)
def scan_schedule_cancel(scan_id):
    return {}


@app.route('/auth', methods=['POST'], cors=cors_config)
def auth():
    response = {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
                 ".eyJzY29wZSI6IjNjZDcwOGNlZmQ1ODQwMWY5ZDQzZmY5NTNmMDYzNDY3IiwiZXhwIjoxNTE1MTUxNTE1fQ"
                 ".UNb9VCWBhVcJgtA1dGl-4QWcBXhfxKgaJuxqIdsBDyc"
    }
    return response


@app.route('/vulns', methods=['GET'], cors=cors_config)
def vulnerability_index():
    response = [
        {
            "oid": "1.3.6.1.4.1.25623.1.0.105879",
            "name": "SSL/TLS: HTTP Strict Transport Security (HSTS) Missing",
            "fix_required": False,
            "threat": "Log"
        }
    ]
    return response


@app.route('/vulns/{oid}', methods=['GET'], cors=cors_config)
def vulnerability_get(oid):
    response = {
        "oid": "1.3.6.1.4.1.25623.1.0.105879",
        "name": "SSL/TLS: HTTP Strict Transport Security (HSTS) Missing",
        "fix_required": False,
        "threat": "Log"
    }
    return response


@app.route('/vulns/{oid}', methods=['PATCH'], cors=cors_config)
def vulnerability_get(oid):
    response = {
        "oid": "1.3.6.1.4.1.25623.1.0.105879",
        "name": "SSL/TLS: HTTP Strict Transport Security (HSTS) Missing",
        "fix_required": False,
        "threat": "Log"
    }
    return response
