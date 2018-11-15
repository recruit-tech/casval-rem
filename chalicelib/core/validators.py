from chalicelib.apis.base import APIBase
from datetime import datetime
from enum import IntFlag
from peewee_validates import BooleanField
from peewee_validates import DateTimeField
from peewee_validates import IntegerField
from peewee_validates import StringField
from peewee_validates import validate_email
from peewee_validates import validate_regexp
from peewee_validates import ValidationError
from peewee_validates import Validator

import binascii
import hashlib
import ipaddress
import os
import pytz
import requests
import socket
import validators

PASSWORD_HASH_ALG = os.environ["PASSWORD_HASH_ALG"]
MAX_COMMENT_LENGTH = int(os.environ["MAX_COMMENT_LENGTH"])
MIN_SCAN_DURATION_IN_SECONDS = 3600 * int(os.environ["MIN_SCAN_DURATION_IN_SECONDS"])
SCAN_SCHEDULABLE_DAYS_FROM_NOW = int(os.environ["SCAN_SCHEDULABLE_DAYS_FROM_NOW"])
SCAN_SCHEDULABLE_DAYS_FROM_START_DATE = int(os.environ["SCAN_SCHEDULABLE_DAYS_FROM_START_DATE"])
AWS_IP_RANGES_URL = os.environ["AWS_IP_RANGES_URL"]


def is_ipv4(value):
    try:
        return validators.ip_address.ipv4(value)
    except Exception:
        return False


def is_public_address(value):
    try:
        return ipaddress.ip_address(value).is_global
    except Exception:
        return False


def is_domain(value):
    try:
        return validators.domain(value)
    except Exception:
        return False


def is_host_resolvable(value):
    try:
        return len(socket.gethostbyname(value)) > 0
    except Exception:
        return False


def valid_ipv4_or_fqdn(field, data):
    if is_ipv4(field.value):
        if not is_public_address(field.value):
            raise Exception("target-is-private-ip")
    elif is_domain(field.value):
        if not is_host_resolvable(field.value):
            raise Exception("could-not-resolve-target-fqdn")
    else:
        raise Exception("target-is-not-fqdn-or-ipv4")


def valid_error_reason(field, data):
    try:
        if field.value.find("-") == -1:
            key = field.value.replace("-", "_")
            if not (key == ""):
                ErrorReasonEnum[key]
        else:
            raise Exception()
    except Exception:
        raise Exception("error_reason_invalid_key")


def password_not_empty(field, data):
    if field.value is True and "password" not in data:
        raise ValidationError("password_not_empty")


class AuditValidator(Validator):
    name = StringField(max_length=128, min_length=1)
    password = StringField(max_length=128, min_length=8)
    submitted = BooleanField()
    ip_restriction = BooleanField()
    password_protection = BooleanField(validators=[password_not_empty])
    rejected_reason = StringField(max_length=128, min_length=1)
    updated_at = DateTimeField()

    @staticmethod
    def get_password_hash(password):
        return binascii.hexlify(
            hashlib.pbkdf2_hmac(
                PASSWORD_HASH_ALG,
                password.encode(),
                os.environ["PASSWORD_SALT"].encode(),
                int(os.environ["PASSWORD_ITERATION"]),
            )
        ).decode("utf-8")

    def clean(self, data):
        if "password" in data:
            data["password"] = self.get_password_hash(data["password"])
        data["updated_at"] = datetime.utcnow()
        return data

    class Meta(object):
        messages = {"password_not_empty": "Password must be provided when enforcing protection."}


class PagenationValidator(Validator):
    page = IntegerField(required=True, low=1, default=1)
    count = IntegerField(
        required=True,
        low=1,
        high=int(os.environ["AUDIT_LIST_MAX_COUNT"]),
        default=int(os.environ["AUDIT_GET_DEFAULT_COUNT"]),
    )


class ContactValidator(Validator):
    name = StringField(required=True, max_length=128, min_length=1, validators=[validate_regexp("^[^,]+$")])
    email = StringField(required=True, max_length=256, validators=[validate_email()])


class ErrorReasonEnum(IntFlag):
    audit_id_not_found = 0
    audit_submitted = 1
    target_is_private_ip = 2
    could_not_resolve_target_fqdn = 3
    target_is_not_fqdn_or_ipv4 = 4

    @property
    def name(self):
        return super().name.replace("_", "-")


class ScanValidator(Validator):
    target = StringField(required=True, validators=[valid_ipv4_or_fqdn])
    start_at = DateTimeField(default=0)
    end_at = DateTimeField(default=0)
    schedule_uuid = StringField()
    scheduled = BooleanField(default=False)
    error_reason = StringField(required=True, validators=[valid_error_reason])
    updated_at = DateTimeField()
    comment = StringField(max_length=MAX_COMMENT_LENGTH, min_length=0)

    @staticmethod
    def is_valid_time_range(start, end):
        start_at = datetime.strptime(start, APIBase.DATETIME_FORMAT)
        start_at = start_at.replace(tzinfo=pytz.utc)
        end_at = datetime.strptime(end, APIBase.DATETIME_FORMAT)
        end_at = end_at.replace(tzinfo=pytz.utc)
        jst = pytz.timezone("Asia/Tokyo")
        now = datetime.now(tz=pytz.utc).astimezone(jst)

        if start_at <= now:
            raise Exception("'start_at has elapsed.")
        if end_at <= now:
            raise Exception("'end_at' has elapsed.")
        if end_at <= start_at:
            raise Exception("'end_at' is equal or earlier than 'start_at'.")

        start_from_now = start_at - now
        if start_from_now.days > SCAN_SCHEDULABLE_DAYS_FROM_NOW:
            raise Exception(
                "'start_at' must be within {} days from now.".format(SCAN_SCHEDULABLE_DAYS_FROM_NOW)
            )

        scan_duration = end_at - start_at
        if scan_duration.days is 0 and scan_duration.seconds < MIN_SCAN_DURATION_IN_SECONDS:
            raise Exception(
                "Duration between 'end_at' and 'start_at' must be equal or more than {} seconds.".format(
                    MIN_SCAN_DURATION_IN_SECONDS
                )
            )
        if scan_duration.days > SCAN_SCHEDULABLE_DAYS_FROM_START_DATE:
            raise Exception(
                "Duration between 'end_at' and 'start_at' within {} days.".format(
                    SCAN_SCHEDULABLE_DAYS_FROM_START_DATE
                )
            )

        return True

    @staticmethod
    def is_AWS(target_ipv4_or_fqdn):
        target_ip_address = socket.gethostbyname(target_ipv4_or_fqdn)
        target_ip_address = ipaddress.ip_address(target_ip_address)
        aws_ip_ranges = requests.get(AWS_IP_RANGES_URL).json()["prefixes"]
        amazon_ip_ranges = [item["ip_prefix"] for item in aws_ip_ranges if item["service"] == "AMAZON"]

        for ip_range in amazon_ip_ranges:
            amazon_network = ipaddress.ip_network(ip_range)
            if target_ip_address in amazon_network:
                return True

        return False

    def clean(self, data):
        data["updated_at"] = datetime.utcnow()
        return data
