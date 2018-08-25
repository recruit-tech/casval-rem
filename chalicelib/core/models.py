from datetime import datetime
from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from peewee import ForeignKeyField
from peewee import Model
from peewee import MySQLDatabase
from peewee import TextField
from peewee import UUIDField

import os
import uuid

db = MySQLDatabase(
    os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_ENDPOINT"],
    port=int(os.environ["DB_PORT"]),
)


class BaseModel(Model):
    class Meta(object):
        database = db


class Audit(BaseModel):
    uuid = UUIDField(unique=True, default=uuid.uuid4)
    name = CharField()
    submitted = BooleanField(default=False)
    ip_restriction = BooleanField(default=True)
    password_protection = BooleanField(default=False)
    password = CharField(default="")
    rejected_reason = CharField(default="")
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Contact(BaseModel):
    audit_id = ForeignKeyField(Audit, backref="contacts", on_delete="CASCADE", on_update="CASCADE")
    name = CharField()
    email = CharField()


class Scan(BaseModel):
    uuid = UUIDField(unique=True, default=uuid.uuid4)
    audit_id = ForeignKeyField(Audit, backref="scans", on_delete="CASCADE", on_update="CASCADE")
    target = CharField()
    start_at = DateTimeField(default=0)
    end_at = DateTimeField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    error_reason = CharField(default="")
    scheduled = BooleanField(default=False)
    schedule_uuid = UUIDField(unique=True, null=True, default=None)
    processed = BooleanField(default=False)
    platform = CharField(default="")
    comment = TextField(default="")


class Vuln(BaseModel):
    oid = CharField(unique=True, null=True, default=None)
    fix_required = BooleanField(null=True)
    name = CharField(null=True)
    cvss_base = CharField(null=True)
    cve = CharField(null=True)
    description = TextField(null=True)


class Result(BaseModel):
    scan_id = ForeignKeyField(Scan, backref="results", on_delete="CASCADE", on_update="CASCADE")
    name = CharField(null=True)
    port = CharField(null=True)
    vuln_id = ForeignKeyField(Vuln, backref="results", on_delete="CASCADE", on_update="CASCADE")
    description = TextField(null=True)
    qod = CharField(null=True)
    severity = CharField(null=True)
    severity_rank = CharField(null=True)
    scanner = CharField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
