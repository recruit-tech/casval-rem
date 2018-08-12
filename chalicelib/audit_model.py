# pyre-strict

from chalicelib.utils.audit_util import AuditDataType
from chalicelib.utils.audit_util import ContentsType
from chalicelib.utils.audit_util import none_to_nullchar
from chalicelib.utils.util import CasvalDateTime
from chalicelib.utils.util import generate_uuid

import boto3
import os

audit_table = boto3.resource("dynamodb", region_name=os.getenv("DYNAMO_REGION")).Table("Audit")

ServiceDataTime: CasvalDateTime = CasvalDateTime()


def get_updated_at_index(
    key, limit: int, forword: bool = False, index: str = "UpdatedAtIndex"
) -> AuditDataType:
    items: AuditDataType = audit_table.query(
        Select="SPECIFIC_ATTRIBUTES",
        ProjectionExpression="id, contacts, scans, rejected_reason,"
        "restricted_by, created_at, updated_at,"
        "#n, #s",
        ExpressionAttributeNames={"#n": "name", "#s": "status"},
        ScanIndexForward=forword,
        IndexName=index,
        KeyConditionExpression=key,
        Limit=limit,
    )
    return items


def get_id(audit_id: str) -> AuditDataType:
    item: AuditDataType = audit_table.get_item(Key={"id": audit_id})
    return item


def save_registering(item: AuditDataType) -> None:
    audit_table.put_item(Item=item)


def save_new_registering(name: str, contacts: ContentsType) -> AuditDataType:
    item: AuditDataType = {
        "id": generate_uuid(),
        "name": name,
        "status": "unsubmitted",
        "contacts": contacts,
        "restricted_by": {"ip": True, "password": False},
        "password": None,
        "rejected_reason": None,
        "created_at": ServiceDataTime.get_now_str(),
        "updated_at": ServiceDataTime.get_now_str(),
    }

    save_registering(item)

    del item["status"]
    del item["password"]
    item["submitted"] = False
    item["scans"] = []
    item = none_to_nullchar(item)
    return item
