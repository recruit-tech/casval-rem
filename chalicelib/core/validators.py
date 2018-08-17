import binascii
import hashlib
import os
from datetime import datetime

from peewee_validates import (BooleanField, DateTimeField, IntegerField,
                              StringField, ValidationError, Validator,
                              validate_email, validate_regexp)

PASSWORD_HASH_ALG = "sha256"


def password_not_empty(field, data):
    if field.value is True and "password" not in data:
        raise ValidationError("password_not_empty")


class AuditValidator(Validator):
    name = StringField(max_length=128, min_length=1)
    password = StringField(max_length=128, min_length=6)
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
