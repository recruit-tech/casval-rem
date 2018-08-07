from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from chalice import BadRequestError
from chalice import NotFoundError
from chalicelib.audit_model import audit_get_id
from chalicelib.audit_model import audit_get_updated_at_index

from chalicelib.audit_util import AUDIT_GET_DEFAULT_COUNT
from chalicelib.audit_util import AUDIT_LIST_MAX_COUNT
from chalicelib.audit_util import AuditMode


def index(app):
    request = app.current_request
    params = request.query_params

    mode: AuditMode = AuditMode.unsubmitted
    count: int = AUDIT_GET_DEFAULT_COUNT
    keys: Key = Key('status').eq(mode.name)

    if params is not None:
        try:
            mode = AuditMode[params["mode"]]
            count = int(params.get("count", AUDIT_GET_DEFAULT_COUNT))

            if count > AUDIT_LIST_MAX_COUNT:
                count = AUDIT_LIST_MAX_COUNT
            try:
                item = audit_get_id(params["before"])
                keys = Key('status').eq(
                    mode.name
                ) & Key('updated_at').lt(
                    item['Item']['updated_at']
                )

            except ClientError as ce:
                if ce.response['Error']['Code'] == 'ResourceNotFoundException':
                    raise NotFoundError("Audit is NotFound")

        except KeyError as e:
            raise BadRequestError(str(e) + "is Unknown key")

    try:
        resp = audit_get_updated_at_index(keys, count)
        return resp

    except ClientError as ce:
        if ce.response['Error']['Code'] == 'ResourceNotFoundException':
            raise NotFoundError("Audit is NotFound")


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
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
                 ".eyJzY29wZSI6IjNjZDcwOGNlZmQ1ODQwMWY"
                 "5ZDQzZmY5NTNmMDYzNDY3IiwiZXhwIjoxNTE"
                 "1MTUxNTE1fQ.UNb9VCWBhVcJgtA1dGl-4QWc"
                 "BXhfxKgaJuxqIdsBDyc"
    }
    return response


def submit(audit_id):
    return {}


def submit_cancel(audit_id):
    return {}
