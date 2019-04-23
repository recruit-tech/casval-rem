from datetime import datetime
from enum import IntFlag

import pytz
from flask_marshmallow import Marshmallow
from marshmallow import post_load
from marshmallow import validate
from marshmallow import validates
from marshmallow import validates_schema

from core import Utils

marshmallow = Marshmallow()

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

AUDIT_LIST_MAX_COUNT = 300
AUDIT_GET_DEFAULT_COUNT = 10
SCAN_MAX_COMMENT_LENGTH = 1000

# FIXME Cloud Pub/Sub doesn't retain queue message more than 7 days
SCAN_SCHEDULABLE_DAYS_FROM_NOW = 10
SCAN_SCHEDULABLE_DAYS_FROM_START_DATE = 5
SCAN_MIN_DURATION_IN_SECONDS = 2 * 3600  # 2 hours


class AuthInputSchema(marshmallow.Schema):
    password = marshmallow.String(required=True, validate=[validate.Length(min=1, max=128)])


class ContactSchema(marshmallow.Schema):
    name = marshmallow.String(required=True, validate=[validate.Length(min=1, max=128)])
    email = marshmallow.String(required=True, validate=[validate.Email(), validate.Length(min=1, max=256)])

    @post_load
    def add_timestamp(self, data):
        data["updated_at"] = datetime.utcnow()
        return data


class PagenationSchema(marshmallow.Schema):
    page = marshmallow.Integer(required=True, validate=[validate.Range(min=1)], default=1)
    count = marshmallow.Integer(
        required=True,
        validate=[validate.Range(min=1, max=AUDIT_LIST_MAX_COUNT)],
        default=AUDIT_GET_DEFAULT_COUNT,
    )


class AuditSchema(marshmallow.Schema):

    name = marshmallow.String(required=True, validate=[validate.Length(min=1, max=128)])
    password = marshmallow.String(required=False, validate=[validate.Length(min=8, max=128)])
    submitted = marshmallow.Boolean(required=True)
    ip_restriction = marshmallow.Boolean(required=True)
    password_protection = marshmallow.Boolean(required=True)
    rejected_reason = marshmallow.String(required=True, validate=[validate.Length(min=1, max=128)])
    updated_at = marshmallow.DateTime(required=True)

    @validates_schema
    def validate_password_presence(field, data):
        if data["password_protection"] == True and "password" not in data:
            raise ValidationError("Password must be provided when enforcing protection")

    @post_load
    def add_timestamp(self, data):
        data["updated_at"] = datetime.utcnow()
        return data


class ScanSchema(marshmallow.Schema):

    target = marshmallow.String(required=True)
    start_at = marshmallow.DateTime(required=True, default=0)
    end_at = marshmallow.DateTime(required=True, default=0)
    schedule_uuid = marshmallow.String(required=True)
    scheduled = marshmallow.Boolean(required=True, default=False)
    updated_at = marshmallow.DateTime(required=True)
    comment = marshmallow.String(
        required=True, validate=[validate.Length(min=0, max=SCAN_MAX_COMMENT_LENGTH)]
    )

    @post_load
    def add_timestamp(self, data):
        data["updated_at"] = datetime.utcnow()
        return data

    class ErrorReasonEnum(IntFlag):
        audit_id_not_found = 0
        audit_submitted = 1
        target_is_private_ip = 2
        could_not_resolve_target_fqdn = 3
        target_is_not_fqdn_or_ipv4 = 4

        @property
        def name(self):
            return super().name.replace("_", "-")

    @validates("target")
    def validate_target(self, value):
        if Utils.is_ipv4(value):
            if not Utils.is_public_address(value):
                raise ValidationError(ErrorReasonEnum.target_is_private_ip.name)
        elif Utils.is_domain(value):
            if not Utils.is_host_resolvable(value):
                raise ValidationError(ErrorReasonEnum.could_not_resolve_target_fqdn.name)
        else:
            raise ValidationError(ErrorReasonEnum.target_is_not_fqdn_or_ipv4.name)

    @validates_schema
    def validate_schedule(self, value):
        if "scheduled" in data and data["scheduled"] == True:
            start_at = datetime.strptime(value["start_at"], DATETIME_FORMAT)
            start_at = start_at.replace(tzinfo=pytz.utc)
            end_at = datetime.strptime(value["end_at"], DATETIME_FORMAT)
            end_at = end_at.replace(tzinfo=pytz.utc)
            jst = pytz.timezone("Asia/Tokyo")
            now = datetime.now(tz=pytz.utc).astimezone(jst)

            if start_at <= now:
                raise ValidationError("'start_at has elapsed.")
            if end_at <= now:
                raise ValidationError("'end_at' has elapsed.")
            if end_at <= start_at:
                raise ValidationError("'end_at' is equal or earlier than 'start_at'.")

            start_from_now = start_at - now
            if start_from_now.days > SCAN_SCHEDULABLE_DAYS_FROM_NOW:
                raise ValidationError(
                    "'start_at' must be within {} days from now.".format(SCAN_SCHEDULABLE_DAYS_FROM_NOW)
                )

            scan_duration = end_at - start_at
            if scan_duration.days is 0 and scan_duration.seconds < SCAN_MIN_DURATION_IN_SECONDS:
                raise ValidationError(
                    "Duration between 'end_at' and 'start_at' must be equal or more than {} seconds.".format(
                        SCAN_MIN_DURATION_IN_SECONDS
                    )
                )
            if scan_duration.days > SCAN_SCHEDULABLE_DAYS_FROM_START_DATE:
                raise ValidationError(
                    "Duration between 'end_at' and 'start_at' within {} days.".format(
                        SCAN_SCHEDULABLE_DAYS_FROM_START_DATE
                    )
                )
