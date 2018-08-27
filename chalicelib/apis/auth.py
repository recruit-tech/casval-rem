from chalicelib.apis.base import APIBase
from chalicelib.core.models import Audit
from chalicelib.core.models import Contact
from chalicelib.core.models import db
from chalicelib.core.models import Result
from chalicelib.core.models import Scan
from chalicelib.core.models import Vuln
from chalicelib.core.validators import AuditValidator

import os


class AuthAPI(APIBase):
    @APIBase.exception_handler
    def __init__(self, app):
        super().__init__(app)
        db.create_tables([Audit, Contact, Scan, Vuln, Result])

    @APIBase.exception_handler
    def auth(self):
        if super()._is_access_permitted() is False:
            raise ConnectionRefusedError("Not allowed to access from your IP addess.")

        body = super()._get_request_body()
        if body is None or "password" not in body:
            raise PermissionError("Password must be specified.")

        password_hash = AuditValidator.get_password_hash(body["password"])
        if password_hash != os.getenv("ADMIN_PASSWORD_HASH"):
            raise PermissionError("Invalid password.")

        token = super()._get_signed_token("*")
        return {"token": token}