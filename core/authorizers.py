from functools import wraps

from flask import abort
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
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
            if identity["scope"] not in [kwargs["audit_uuid"], "*"]:
                abort(401, "Token is invalid for the audit")
            else:
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
