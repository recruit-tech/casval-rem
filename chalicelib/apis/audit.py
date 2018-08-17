import datetime
import logging
import os

import jwt
from chalice import BadRequestError, NotFoundError, UnauthorizedError
from peewee import fn

from chalicelib.apis.base import APIBase
from chalicelib.core.models import Audit, Contact, db
from chalicelib.core.validators import (AuditPagenationValidator,
                                        AuditValidator, ContactValidator)

TOKEN_EXPIRATION_IN_HOUR = 3


class AuditAPI(APIBase):
    def __init__(self, app):
        super().__init__(app)

    def index(self):
        try:
            params = super()._get_query_params()
            page_validator = AuditPagenationValidator()
            page_validator.validate(params)
            if page_validator.errors:
                raise Exception(page_validator.errors)
            count = page_validator.data["count"]
            page = page_validator.data["page"]
            submitted = False
            if params.get("mode") == "submitted":
                submitted = True

            audits = (
                Audit.select(
                    Audit,
                    fn.GROUP_CONCAT(Contact.name).alias("contact_names"),
                    fn.GROUP_CONCAT(Contact.email).alias("contact_emails"),
                )
                .where(Audit.submitted == submitted)
                .join(Contact, on=(Audit.id == Contact.audit_id))
                .group_by(Audit.id)
                .order_by(Audit.updated_at.desc())
                .paginate(page, count)
            )

            response = []
            for audit in audits.dicts():
                entry = {}
                entry["id"] = audit["id"]
                entry["uuid"] = audit["uuid"].hex
                entry["name"] = audit["name"]
                entry["submitted"] = audit["submitted"]
                entry["ip_restriction"] = audit["ip_restriction"]
                entry["password_protection"] = audit["password_protection"]
                entry["rejected_reason"] = audit["rejected_reason"]
                # TODO: Change to UTC
                entry["created_at"] = audit["created_at"].strftime(APIBase.RESPONSE_TIME_FORMAT)
                # TODO: Change to UTC
                entry["updated_at"] = audit["updated_at"].strftime(APIBase.RESPONSE_TIME_FORMAT)
                entry["contact_names"] = audit["contact_names"].split(",")
                entry["contact_emails"] = audit["contact_emails"].split(",")
                response.append(entry)

            return response

        except Exception as e:
            self.app.log.error(e)
            raise BadRequestError(e)

    def get(self, audit_uuid):
        try:
            return self.__get_audit_by_uuid(audit_uuid)
        except IndexError as e:
            self.app.log.error(e)
            raise NotFoundError(e)
        except Exception as e:
            self.app.log.error(e)
            raise BadRequestError(e)

    def post(self):
        try:
            body = super()._get_request_body()
            with db.atomic():
                audit_validator = AuditValidator()
                audit_validator.validate({"name": body["name"]}, only=("name"))
                if audit_validator.errors:
                    raise Exception(audit_validator.errors)
                audit = Audit(name=audit_validator.data["name"])
                audit.save()

                if "contacts" not in body or len(body["contacts"]) is 0:
                    raise BadRequestError("'contacts': Must be contained.")
                contact_validator = ContactValidator()
                contacts = body["contacts"]

                for contact in contacts:
                    contact_validator.validate(contact)
                    if contact_validator.errors:
                        raise Exception(contact_validator.errors)
                    contact["audit_id"] = audit.id
                Contact.insert_many(contacts).execute()

            return self.__get_audit_by_uuid(audit.uuid)

        except Exception as e:
            self.app.log.error(e)
            raise BadRequestError(e)

    def patch(self, audit_uuid):
        try:
            body = super()._get_request_body()
            audit = self.__get_audit_by_uuid(audit_uuid, raw=True)

            with db.atomic():
                key_filter = ("name", "ip_restriction", "password_protection", "password")
                audit_new = {k: v for k, v in body.items() if k in key_filter}
                if audit_new:
                    audit_validator = AuditValidator()
                    audit_validator.validate(audit_new, only=audit_new)
                    if audit_validator.errors:
                        raise Exception(audit_validator.errors)
                    Audit.update(audit_validator.data).where(Audit.id == audit["id"]).execute()

                if "contacts" in body:
                    if len(body["contacts"]) is 0:
                        raise Exception("'contents': Must be contained.")
                    contacts_new = body["contacts"]
                    contact_validator = ContactValidator()

                    for contact_new in contacts_new:
                        contact_new["audit_id"] = audit["id"]
                        contact_validator.validate(contact_new)
                        if contact_validator.errors:
                            raise Exception(contact_validator.errors)
                    Contact.delete().where(Contact.audit_id == audit["id"]).execute()
                    Contact.insert_many(contacts_new).execute()

            return self.__get_audit_by_uuid(audit_uuid)

        except IndexError as e:
            self.app.log.error(e)
            raise NotFoundError(e)
        except Exception as e:
            self.app.log.error(e)
            raise BadRequestError(e)

    def delete(self, audit_uuid):
        try:
            query = Audit.delete().where(Audit.uuid == audit_uuid)
            row_count = query.execute()
            if row_count == 0:
                raise IndexError("'audit_uuid': Item could not be found.")
            return {}

        except IndexError as e:
            self.app.log.error(e)
            raise NotFoundError(e)
        except Exception as e:
            self.app.log.error(e)
            raise BadRequestError(e)

    def tokens(self, audit_uuid):
        try:
            audit = self.__get_audit_by_uuid(audit_uuid, raw=True)

            if audit["ip_restriction"] is True:
                if not super()._is_access_permitted():
                    raise ConnectionRefusedError("Not allowed to access from your IP addess.")

            if audit["password_protection"] is True:
                body = super()._get_request_body()
                if body is None or "password" not in body:
                    raise PermissionError("Password must be specified.")
                password_hash = AuditValidator.get_password_hash(body["password"])
                if password_hash != audit["password"]:
                    raise PermissionError("Invalid password.")

            expiration_time = datetime.datetime.now() + datetime.timedelta(hours=TOKEN_EXPIRATION_IN_HOUR)
            ext = expiration_time.strftime("%s")
            claim = {"scope": audit_uuid, "exp": ext}
            token = jwt.encode(claim, os.getenv("JWT_SECRET"), algorithm="HS256")
            response = {"token": token.decode("utf-8")}
            return response

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

    def submit(self, audit_uuid):
        try:
            audit = self.__get_audit_by_uuid(audit_uuid)

            # TODO: Check if number of scan belongging to the audit is more than 1
            # TODO: Check if status of all scan is processed=true
            # TODO: Check if no fix-required in a result of all scans, if fix-required,
            #       length of the comment is more than 1

            submitted = {"submitted": True}
            Audit.update(submitted).where(Audit.uuid == audit_uuid).execute()

            return self.__get_audit_by_uuid(audit_uuid)

        except IndexError as e:
            self.app.log.error(e)
            raise NotFoundError(e)
        except Exception as e:
            self.app.log.error(e)
            raise BadRequestError(e)

    def submit_cancel(self, audit_uuid):
        try:
            body = super()._get_request_body()

            unsubmitted = {"submitted": False}
            if "rejected_reason" in body:
                unsubmitted["rejected_reason"] = body["rejected_reason"]

            audit_validator = AuditValidator()
            audit_validator.validate(unsubmitted, unsubmitted)
            if audit_validator.errors:
                raise Exception(audit_validator.errors)
            Audit.update(audit_validator.data).where(Audit.uuid == audit_uuid).execute()

            return self.__get_audit_by_uuid(audit_uuid)

        except IndexError as e:
            self.app.log.error(e)
            raise NotFoundError(e)
        except Exception as e:
            self.app.log.error(e)
            raise BadRequestError(e)

    def __get_audit_by_uuid(self, uuid, raw=False):
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
            # TODO: Change to UTC
            response["created_at"] = audit["created_at"].strftime(APIBase.RESPONSE_TIME_FORMAT)
            # TODO: Change to UTC
            response["updated_at"] = audit["updated_at"].strftime(APIBase.RESPONSE_TIME_FORMAT)
            response["contacts"] = []

            for contact in audits[0].contacts.dicts():
                response["contacts"].append({"name": contact["name"], "email": contact["email"]})

            response["scans"] = []  # ToDo: Return actual scans

            return response
