import os
import jwt
import datetime
import ipaddress

from chalice import BadRequestError, UnauthorizedError, NotFoundError
from chalicelib.core.models import db, Audit, Contact
from chalicelib.core.validators import AuditValidator, ContactValidator
from peewee import *

import logging
logger = logging.getLogger('peewee')
#logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def index(app):
    response = {
        "name": "コーポレートサイト",
        "contacts": [{"name": "nishimunea", "email": "nishimunea@example.jp"}],
        "id": "3cd708cefd58401f9d43ff953f063467",
        "scans": ["21d6cd7b33e84fbf9a2898f4ea7f90cc"],
        "submitted": False,
        "rejected_reason": "深刻な脆弱性が修正されていません",
        "restricted_by": {"ip": True, "password": False},
        "created_at": "2018-10-10 23:59:59",
        "updated_at": "2018-10-10 23:59:59",
    }
    return response


def get(app, audit_id):
    try:
        response = __get_audit(audit_id)
        return response
    except IndexError as e:
        app.log.error(e)
        raise NotFoundError(e)
    except Exception as e:
        app.log.error(e)
        raise BadRequestError(e)

def post(app):
    try:
        body = app.current_request.json_body
        with db.atomic():
            audit_validator = AuditValidator()
            audit_validator.validate({"name": body["name"]}, only=('name'))
            if audit_validator.errors:
                raise Exception(audit_validator.errors)
            audit = Audit(name = audit_validator.data)
            audit.save()

            if "contacts" not in body or len(body["contacts"]) is 0:
                raise BadRequestError("'contents': Must be contained.")
            contact_validator = ContactValidator()
            contacts = body["contacts"]

            for contact in contacts:
                contact["audit_id"] = audit.id
                contact_validator.validate(contact)
                if contact_validator.errors:
                    raise Exception(contact_validator.errors)
            Contact.insert_many(contacts).execute()

        response = __get_audit(audit.uuid)
        return response

    except Exception as e:
        app.log.error(e)
        raise BadRequestError(e)


def __get_audit(uuid):
    audits = Audit.select().where(Audit.uuid==uuid)
    audit = audits.dicts()[0]
    response = {}
    response["uuid"] = audit["uuid"].hex
    response["name"] = audit["name"]
    response["submitted"] = audit["submitted"]
    response["ip_restriction"] = audit["ip_restriction"]
    response["password_protection"] = audit["password_protection"]
    response["rejected_reason"] = audit["rejected_reason"]
    response["created_at"] = audit["created_at"].strftime("%Y-%m-%d %H:%M:%S") # TODO: Change to UTC
    response["updated_at"] = audit["updated_at"].strftime("%Y-%m-%d %H:%M:%S") # TODO: Change to UTC
    response["contacts"] = []
    # TODO: backref may require an additional db access to audits[0]
    for contact in audits[0].contacts.dicts():
        response["contacts"].append({"name": contact["name"], "email": contact["email"]})
    response["scans"] = [] # ToDo: Return actual scans
    return response


def patch(app, audit_uuid):
    try:
        body = app.current_request.json_body
        audit_id = __get_audit_id(audit_uuid)

        with db.atomic():
            audit = {k:v for k, v in body.items() if k in ('name', 'ip_restriction', 'password_protection', 'password')}
            if audit:
                audit_validator = AuditValidator()
                audit_validator.validate(audit, only=audit)
                if audit_validator.errors:
                    raise Exception(audit_validator.errors)
                Audit.update(audit_validator.data).where(Audit.id == audit_id).execute()

            if "contacts" in body:
                if len(body["contacts"]) is 0:
                    raise BadRequestError("'contents': Must be contained.")
                contact_validator = ContactValidator()
                contacts = body["contacts"]

                for contact in contacts:
                    contact["audit_id"] = audit_id
                    contact_validator.validate(contact)
                    if contact_validator.errors:
                        raise Exception(contact_validator.errors)
                Contact.delete().where(Contact.audit_id == audit_id).execute()
                Contact.insert_many(contacts).execute()

        response = __get_audit(audit_uuid)
        return response

    except IndexError as e:
        app.log.error(e)
        raise NotFoundError(e)
    except Exception as e:
        app.log.error(e)
        raise BadRequestError(e)

def delete(app, audit_id):
    try:
        query = Audit.delete().where(Audit.uuid == audit_id)
        row_count = query.execute()
        if row_count == 0:
            raise IndexError("'audit_id': Item could not be found.")
        return {}
    except IndexError as e:
        app.log.error(e)
        raise NotFoundError(e)
    except Exception as e:
        app.log.error(e)
        raise BadRequestError(e)


def tokens(app, audit_uuid):
    audits = Audit.select().where(Audit.uuid==audit_uuid).dicts()
    if len(audits) is 0:
        raise IndexError("'audit_uuid': Item could not be found.")
    audit = audits[0]

    if audit["ip_restriction"]:
        source_ip_address = app.current_request.context["identity"]["sourceIp"]
        if not __is_permitted_ip_address(source_ip_address):
            raise UnauthorizedError("Not allowed to access from your IP addess.")

    if audit["password_protection"]:
        body = app.current_request.json_body
        if body is None or "password" not in body:
            raise UnauthorizedError("Password must be specified.")
        password_hash = AuditValidator.get_password_hash(body["password"])
        if password_hash.decode("utf-8") != audit["password"]:
            raise UnauthorizedError("Invalid password.")

    expiration_time = datetime.datetime.now() + datetime.timedelta(hours=24)
    ext = expiration_time.strftime("%s")
    claim = {"scope": audit_uuid, "exp": ext}
    token = jwt.encode(claim, os.environ["JWT_SECRET"], algorithm="HS256")
    response = {"token": token.decode("utf-8")}
    return response


def __is_permitted_ip_address(ip_address):
    try:
        permitted_ip_ranges = os.getenv("PERMITTED_IP_ADDRESS_RANGE").split(',')
        source_ip_address = ipaddress.ip_address(ip_address)
        for permitted_ip_range in permitted_ip_ranges:
            permitted_ip_network = ipaddress.ip_network(permitted_ip_range)
            if source_ip_address in permitted_ip_network:
                return True
        return False
    except Exception as e:
        app.log.error(e)
        return False


def submit(app, audit_uuid):
    try:
        body = app.current_request.json_body
        audit_id = __get_audit_id(audit_uuid)

        #TODO: Check if number of scan belongging to the audit is more than 1
        #TODO: Check if status of all scan is processed=true
        #TODO: Check if no fix-required in a result of all scans, if fix-required, length of the comment is more than 1

        Audit.update({"submitted": True}).where(Audit.id == audit_id).execute()

        response = __get_audit(audit_uuid)
        return response

    except IndexError as e:
        app.log.error(e)
        raise NotFoundError(e)
    except Exception as e:
        app.log.error(e)
        raise BadRequestError(e)


# Change to __get_audit_by_uuid
def __get_audit_id(audit_uuid):
    audits = Audit.select().where(Audit.uuid==audit_uuid).dicts()
    if len(audits) is 0:
        raise IndexError("'audit_uuid': Item could not be found.")
    return audits[0]["id"]


def submit_cancel(app, audit_uuid):
    try:
        body = app.current_request.json_body
        audit_id = __get_audit_id(audit_uuid)

        diff = {"submitted": False}
        if "rejected_reason" in body:
            diff["rejected_reason"] = body["rejected_reason"]

        audit_validator = AuditValidator()
        audit_validator.validate(diff, diff)
        if audit_validator.errors:
            raise Exception(audit_validator.errors)
        Audit.update(audit_validator.data).where(Audit.id == audit_id).execute()

        response = __get_audit(audit_uuid)
        return response

    except IndexError as e:
        app.log.error(e)
        raise NotFoundError(e)
    except Exception as e:
        app.log.error(e)
        raise BadRequestError(e)

