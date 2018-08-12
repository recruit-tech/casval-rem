# pyre-strict

from datetime import datetime
from datetime import timedelta

import os
import uuid

# define
AHEAD_TIME: int = int(os.getenv("AHEAD_TIME"))  # pyre-ignore[6]


class ValidationError(Exception):
    """Exception class for ValidationError"""

    def __init__(self, msg: str) -> None:
        Exception.__init__(self, msg)  # pyre-ignore[19]
        self.msg: str = msg

    def get_message(self) -> str:
        return self.msg


class CasvalDateTime(object):
    """Time used for service for class"""

    def __init__(self, deltatime: int = AHEAD_TIME, output_format: str = "%Y-%m-%d %H:%M:%S") -> None:

        self.deltatime: int = deltatime
        self.output_format: str = output_format

    def set_hours_ahead(self, deltatime: int) -> None:
        self.deltatime = deltatime

    def set_output_format(self, output_format: str) -> None:
        self.output_format = output_format

    def get_now(self) -> datetime:
        return datetime.now() + timedelta(hours=self.deltatime)

    def get_now_str(self) -> str:
        return self.get_now().strftime("%Y-%m-%d %H:%M:%S")

    def str_to_time(self, time: str) -> datetime:
        return datetime.strptime(time, self.output_format)

    def time_to_str(self, time: datetime) -> str:
        return time.strftime(self.output_format)


def generate_uuid() -> str:
    return str(uuid.uuid4().hex)
