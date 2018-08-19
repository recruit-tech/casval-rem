from chalicelib.apis.base import APIBase
from chalicelib.core.models import Audit, Contact, Scan, db


class AuthenticationAPI(APIBase):
    @APIBase.exception_handler
    def __init__(self, app):
        super().__init__(app)
        db.create_tables([Audit, Contact, Scan])

    @APIBase.exception_handler
    def authenticate(self):
        # IP restriction required through decorator
        response = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
            ".eyJzY29wZSI6IioiLCJleHAiOjE2MDIyNTU2MDB9"
            ".zvz-IMMCXA_VCwElPE3BsrpPVnicSw0YFdsDi4wjyeo"
        }

        return response
