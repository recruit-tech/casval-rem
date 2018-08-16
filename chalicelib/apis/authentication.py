from chalicelib.core.models import Audit, Contact, Scan, db

class AuthenticationAPI:

    def __init__(self, app):
        db.create_tables([Audit, Contact, Scan])
        self.app = app


    def authenticate(self):
        response = {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
            ".eyJzY29wZSI6IioiLCJleHAiOjE2MDIyNTU2MDB9"
            ".zvz-IMMCXA_VCwElPE3BsrpPVnicSw0YFdsDi4wjyeo"
        }

        return response
