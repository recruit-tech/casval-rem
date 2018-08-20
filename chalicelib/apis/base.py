from chalice import BadRequestError
from chalice import ForbiddenError
from chalice import NotFoundError
from chalice import UnauthorizedError
from chalicelib.core.models import Audit

import datetime
import ipaddress
import jwt
import logging
import os


logger = logging.getLogger("peewee")
# logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

TOKEN_EXPIRATION_IN_HOUR = 3


class APIBase(object):

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, app):
        self.app = app

    def _get_query_params(self):
        params = self.app.current_request.query_params
        return params if params is not None else {}

    def _get_request_body(self):
        body = self.app.current_request.json_body
        return body if body is not None else {}

    def _is_access_permitted(self):
        try:
            source_ip = self.app.current_request.context["identity"]["sourceIp"]
            permitted_ip_ranges = os.getenv("PERMITTED_IP_ADDRESS_RANGE").split(",")
            source_ip = ipaddress.ip_address(source_ip)

            for permitted_ip_range in permitted_ip_ranges:
                permitted_ip_network = ipaddress.ip_network(permitted_ip_range)
                if source_ip in permitted_ip_network:
                    return True

            return False

        except Exception as e:
            self.app.log.error(e)
            return False

    def _get_audit_by_uuid(self, uuid, raw=False):
        audits = Audit.select().where(Audit.uuid == uuid)
        audit = audits.dicts()[0]

        if raw is True:
            return audit

        else:
            response = {}
            response["uuid"] = audit["uuid"].hex
            response["name"] = audit["name"]
            response["submitted"] = audit["submitted"]
            response["ip_restriction"] = audit["ip_restriction"]
            response["password_protection"] = audit["password_protection"]
            response["rejected_reason"] = audit["rejected_reason"]
            response["created_at"] = audit["created_at"].strftime(APIBase.DATETIME_FORMAT)
            response["updated_at"] = audit["updated_at"].strftime(APIBase.DATETIME_FORMAT)
            response["contacts"] = []

            for contact in audits[0].contacts.dicts():
                response["contacts"].append({"name": contact["name"], "email": contact["email"]})

            response["scans"] = []
            for scan in audits[0].scans.dicts():
                response["scans"].append(scan["uuid"].hex)

            return response

    def _get_signed_token(self, scope):
        expiration_time = datetime.datetime.now() + datetime.timedelta(hours=TOKEN_EXPIRATION_IN_HOUR)
        ext = expiration_time.strftime("%s")
        claim = {"scope": scope, "exp": ext}
        token = jwt.encode(claim, os.getenv("JWT_SECRET"), algorithm="HS256")
        return token.decode("utf-8")

    @classmethod
    def exception_handler(cls, func):
        def self_wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except ConnectionRefusedError as e:
                self.app.log.error(e)
                raise ForbiddenError(e)
            except PermissionError as e:
                self.app.log.error(e)
                raise UnauthorizedError(e)
            except IndexError as e:
                self.app.log.error(e)
                raise NotFoundError(e)
            except Exception as e:
                self.app.log.error(e)
                raise BadRequestError(e)

        return self_wrapper
