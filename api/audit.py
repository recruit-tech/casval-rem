def index():
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


def get(audit_id):
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


def post():
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


def patch(audit_id):
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


def delete(audit_id):
    return {}


def tokens(audit_id):
    response = {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
                 ".eyJzY29wZSI6IjNjZDcwOGNlZmQ1ODQwMWY5ZDQzZmY5NTNmMDYzNDY3IiwiZXhwIjoxNjAyMjU1NjAwfQ._"
                 "-oZkuBL5yj8_bjioz1YQHicZkrjp7JBR0DpO6yNFew"
    }
    return response


def submit(audit_id):
    return {}


def submit_cancel(audit_id):
    return {}
