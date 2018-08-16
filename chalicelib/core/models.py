from peewee import *

import os
import uuid
from datetime import datetime


db = MySQLDatabase(
    os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_ENDPOINT"],
    port=int(os.environ["DB_PORT"]))


class BaseModel(Model):
    class Meta:
        database = db


class Audit(BaseModel):
    uuid = UUIDField(unique=True, default=uuid.uuid4)
    name = CharField()
    submitted = BooleanField(default=False)
    ip_restriction = BooleanField(default=True)
    password_protection = BooleanField(default=False)
    password = CharField(default="")
    rejected_reason = CharField(default="")
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)


class Contact(BaseModel):
    audit_id = ForeignKeyField(Audit, backref='contacts', on_delete="CASCADE", on_update="CASCADE")
    name = CharField()
    email = CharField()


class Scan(BaseModel):
    uuid = UUIDField(unique=True, default=uuid.uuid4)
    audit_id = ForeignKeyField(Audit, backref='scans', on_delete="CASCADE", on_update="CASCADE")
    target = CharField()
    start_at = DateTimeField(default=datetime.now)
    end_at = DateTimeField(default=datetime.now)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    error_reason = CharField(default="")
    scheduled = BooleanField(default=False)
    processed = BooleanField(default=False)
    platform = CharField(default="")
    report_url = CharField(default="")
    comment = TextField(default="")
