import binascii
import hashlib
import ipaddress
import os
import socket
from datetime import datetime

import requests
import validators
from peewee_validates import (BooleanField, DateTimeField, IntegerField,
                              StringField, ValidationError, Validator,
                              validate_email, validate_regexp)

PASSWORD_HASH_ALG = "sha256"
MAX_COMMENT_LENGTH = 1000
AWS_IP_RANGES_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"


def is_ipv4(value):
    try:
        return validators.ip_address.ipv4(value)
    except Exception as e:
        return False


def is_public_address(value):
    try:
        return ipaddress.ip_address(value).is_global
    except Exception as e:
        return False


def is_domain(value):
    try:
        return validators.domain(value)
    except Exception as e:
        return False


def is_host_resolvable(value):
    try:
        return len(socket.gethostbyname(value)) > 0
    except Exception as e:
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
        data["updated_at"] = datetime.now()
        return data

    class Meta:
        messages = {"password_not_empty": "Password must be provided when enforcing protection."}


class AuditPagenationValidator(Validator):
    page = IntegerField(required=True, low=1, default=1)
    count = IntegerField(required=True, low=1, high=300, default=30)


class ContactValidator(Validator):
    name = StringField(required=True, max_length=128, min_length=1, validators=[validate_regexp("^[^,]+$")])
    email = StringField(required=True, max_length=256, validators=[validate_email()])


class ScanValidator(Validator):
    target = StringField(required=True, validators=[valid_ipv4_or_fqdn])
    updated_at = DateTimeField()
    comment = StringField(max_length=MAX_COMMENT_LENGTH, min_length=1)

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
        data["updated_at"] = datetime.now()
        return data
