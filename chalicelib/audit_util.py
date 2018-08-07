from enum import IntEnum
import os

# define
AUDIT_GET_DEFAULT_COUNT = int(os.getenv("AUDIT_GET_DEFAULT_COUNT"))
AUDIT_LIST_MAX_COUNT = int(os.getenv("AUDIT_LIST_MAX_COUNT"))


class AuditMode(IntEnum):
    unsubmitted = 0
    submitted = 1
