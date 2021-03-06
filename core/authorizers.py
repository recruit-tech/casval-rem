from functools import wraps

from flask import abort
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import get_raw_jwt
from flask_jwt_extended import verify_jwt_in_request

jwt = JWTManager()


class Authorizer:
    def token_required(f):
        @wraps(f)
        def decorate(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
            except:
                abort(401, "Token is invalid")

            if identity["restricted"] == False:
                jwt = get_raw_jwt()
                if "exp" not in jwt:
                    abort(401, "Expiration time (exp) must be set if token type is NOT restricted")

            if "audit_uuid" in kwargs:
                if identity["restricted"] == True:
                    abort(401, "Token is restricted to access of the audit")
                if identity["scope"] not in [kwargs["audit_uuid"], "*"]:
                    abort(401, "Token is invalid for the audit")

            if "scan_uuid" in kwargs:
                audit_uuid = kwargs["scan_uuid"][0:24] + "0" * 8
                if identity["scope"] not in [audit_uuid, "*"]:
                    abort(401, "Token is invalid for the scan")

            return f(*args, **kwargs)

        return decorate

    def admin_token_required(f):
        @wraps(f)
        def decorate(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
            except:
                abort(401, "Token is invalid")
            if identity["scope"] != "*":
                abort(401, "Token is insufficient privileges")
            else:
                return f(*args, **kwargs)

        return decorate
