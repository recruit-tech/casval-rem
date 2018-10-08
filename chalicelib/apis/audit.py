from chalice import Response
from chalicelib.apis.base import APIBase
from chalicelib.core.models import Audit
from chalicelib.core.models import Contact
from chalicelib.core.models import db
from chalicelib.core.models import Result
from chalicelib.core.models import Scan
from chalicelib.core.models import Vuln
from chalicelib.core.validators import AuditValidator
from chalicelib.core.validators import ContactValidator
from chalicelib.core.validators import PagenationValidator
from peewee import fn

import csv
import tempfile

AUDIT_DOWNLOAD_COLUMNS = [
    "target",
    "port",
    "name",
    "cve",
    "cvss_base",
    "severity_rank",
    "fix_required",
    "description",
    "oid",
    "created_at",
    "comment",
]


class AuditAPI(APIBase):
    @APIBase.exception_handler
    def __init__(self, app):
        super().__init__(app)

    @APIBase.exception_handler
    def index(self):
        params = super()._get_query_params()
        page_validator = PagenationValidator()
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
            entry = {
                "id": audit["id"],
                "uuid": audit["uuid"].hex,
                "name": audit["name"],
                "submitted": audit["submitted"],
                "ip_restriction": audit["ip_restriction"],
                "password_protection": audit["password_protection"],
                "rejected_reason": audit["rejected_reason"],
                "created_at": audit["created_at"].strftime(APIBase.DATETIME_FORMAT),
                "updated_at": audit["updated_at"].strftime(APIBase.DATETIME_FORMAT),
                "contact_names": audit["contact_names"].split(","),
                "contact_emails": audit["contact_emails"].split(","),
            }
            response.append(entry)

        return response

    @APIBase.exception_handler
    def get(self, audit_uuid):
        return super()._get_audit_by_uuid(audit_uuid)

    @APIBase.exception_handler
    def post(self):
        body = super()._get_request_body()
        with db.atomic():
            audit_validator = AuditValidator()
            audit_validator.validate({"name": body["name"]}, only=("name"))
            if audit_validator.errors:
                raise Exception(audit_validator.errors)
            audit = Audit(name=audit_validator.data["name"])
            audit.save()

            if "contacts" not in body or len(body["contacts"]) is 0:
                raise Exception("'contacts': Must be contained.")
            contact_validator = ContactValidator()
            contacts = body["contacts"]

            for contact in contacts:
                contact_validator.validate(contact)
                if contact_validator.errors:
                    raise Exception(contact_validator.errors)
                contact["audit_id"] = audit.id
            Contact.insert_many(contacts).execute()

        return super()._get_audit_by_uuid(audit.uuid)

    @APIBase.exception_handler
    def patch(self, audit_uuid):
        body = super()._get_request_body()
        audit = super()._get_audit_by_uuid(audit_uuid, raw=True)

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

        return super()._get_audit_by_uuid(audit_uuid)

    @APIBase.exception_handler
    def delete(self, audit_uuid):
        query = Audit.delete().where(Audit.uuid == audit_uuid)
        row_count = query.execute()
        if row_count == 0:
            raise IndexError("'audit_uuid': Item could not be found.")
        return {}

    @APIBase.exception_handler
    def tokens(self, audit_uuid):
        audit = super()._get_audit_by_uuid(audit_uuid, raw=True)

        if audit["ip_restriction"] is True:
            if not super()._is_access_permitted():
                raise ConnectionRefusedError("Not allowed to access from your IP address.")

        if audit["password_protection"] is True:
            body = super()._get_request_body()
            if body is None or "password" not in body:
                raise PermissionError("Password must be specified.")
            password_hash = AuditValidator.get_password_hash(body["password"])
            if password_hash != audit["password"]:
                raise PermissionError("Invalid password.")

        token = super()._get_signed_token(audit_uuid)
        return {"token": token}

    @APIBase.exception_handler
    def submit(self, audit_uuid):
        super()._get_audit_by_uuid(audit_uuid)
        submitted = {"submitted": True}
        Audit.update(submitted).where(Audit.uuid == audit_uuid).execute()

        return super()._get_audit_by_uuid(audit_uuid)

    @APIBase.exception_handler
    def submit_cancel(self, audit_uuid):
        body = super()._get_request_body()

        unsubmitted = {"submitted": False}
        if "rejected_reason" in body:
            unsubmitted["rejected_reason"] = body["rejected_reason"]

        audit_validator = AuditValidator()
        audit_validator.validate(unsubmitted, unsubmitted)
        if audit_validator.errors:
            raise Exception(audit_validator.errors)
        Audit.update(audit_validator.data).where(Audit.uuid == audit_uuid).execute()

        return super()._get_audit_by_uuid(audit_uuid)

    @APIBase.exception_handler
    def download(self, audit_uuid):
        audits = Audit.select().where(Audit.uuid == audit_uuid)

        scan_ids = []
        for scan in audits[0].scans.dicts():
            if scan["processed"] is True:
                scan_ids.append(scan["id"])

        results = (
            Result.select(Result, Scan, Vuln)
            .join(Scan)
            .join(Vuln, on=(Result.vuln_id == Vuln.oid))
            .where(Result.scan_id.in_(scan_ids))
            .order_by(Result.scan_id)
        )

        with tempfile.TemporaryFile("r+") as f:
            writer = csv.DictWriter(f, AUDIT_DOWNLOAD_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for result in results.dicts():
                writer.writerow(result)
            f.flush()
            f.seek(0)
            output = f.read()

        headers = {"Content-Type": "text/csv"}
        return Response(body=output, headers=headers, status_code=200)
