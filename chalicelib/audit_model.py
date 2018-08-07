import boto3
import os

audit_table = boto3.resource("dynamodb", region_name=os.getenv("DYNAMO_REGION")).Table("Audit")


def audit_get_updated_at_index(key, limit, forword=False, index="UpdatedAtIndex"):
    items = audit_table.query(
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


def audit_get_id(audit_id):
    return audit_table.get_item(Key={"id": audit_id})
