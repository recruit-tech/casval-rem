# pyre-strict

from chalicelib.utils.util import ValidationError
from datetime import datetime
from enum import IntEnum
from typing import Any
from typing import Dict
from typing import List
from typing import Union
from validate_email import validate_email

import os

# audit type hints
ENVType = int
ContentsType = List[Dict[str, str]]
RestrictByType = Dict[str, bool]

# DBに空文字列が入れれないのでNoneで代用してるので許容
AuditDataType = Dict[str, Union[str, ContentsType, RestrictByType, datetime, bool, None]]
APIResultType = Union[Any, AuditDataType]

# define
# "pyre-ignore[6]" 型のつけ方が間違っているというエラーだが，そもそもintなので変換エラーしかありえないというバグを踏んだ
AUDIT_GET_DEFAULT_COUNT: ENVType = int(os.getenv("AUDIT_GET_DEFAULT_COUNT"))  # pyre-ignore[6]
AUDIT_LIST_MAX_COUNT: ENVType = int(os.getenv("AUDIT_LIST_MAX_COUNT"))  # pyre-ignore[6]
AUDIT_NAME_MAX_LENGTH: ENVType = int(os.getenv("AUDIT_NAME_MAX_LENGTH"))  # pyre-ignore[6]


class AuditMode(IntEnum):
    unsubmitted: int = 0  # pyre-ignore[8]
    submitted: int = 1  # pyre-ignore[8]


def validate_contacts(_contacts: ContentsType) -> ContentsType:
    contacts: ContentsType = []
    for content in _contacts:
        name = content["name"]
        email = content["email"]
        # ignore[16]はvalidate_emailがただの関数でなおかつアノテーションがないということに起因するバグ
        if not validate_email(email):  # pyre-ignore[16]
            raise ValidationError("Invalid email: {0}".format(email))

        contacts.append({"name": validate_name(name), "email": email})

    return contacts


def validate_name(_name: str) -> str:
    name = trim_whitespace(_name)
    name_size = len(name)
    if name_size == 0:
        raise ValidationError("Invalid name: {0}".format(name))
    if name_size > AUDIT_NAME_MAX_LENGTH:
        raise ValidationError("Invalid name: {0}".format(name))

    return name


def trim_whitespace(_name: str) -> str:
    return _name.rstrip()


def none_to_nullchar(item: AuditDataType) -> AuditDataType:
    keys = item.keys()
    for key in keys:
        if item[key] is None:
            item[key] = ""

    return item
