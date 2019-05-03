import csv
import tempfile

from flask import Response
from flask import abort
from flask import request
from flask_jwt_extended import create_access_token
from flask_restplus import Namespace
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from peewee import fn

from core import AuditInputSchema
from core import AuditListInputSchema
from core import AuditResource
from core import AuditTable
from core import AuditTokenInputSchema
from core import AuditUpdateSchema
from core import Authorizer
from core import ContactSchema
from core import ContactTable
from core import PendingTask
from core import ResultTable
from core import ScanInputSchema
from core import ScanResource
from core import ScanTable
from core import ScanUpdateSchema
from core import Utils
from core import VulnTable
from core import db

api = Namespace("audit")

ContactModel = api.model(
    "ContactModel", {"name": fields.String(required=True), "email": fields.String(required=True)}
)

AuditOutputModel = api.model(
    "AuditOutputModel",
    {
        "id": fields.Integer(required=True),
        "uuid": fields.String(required=True, attribute=lambda audit: audit["uuid"].hex),
        "name": fields.String(required=True),
        "submitted": fields.Boolean(required=True),
        "approved": fields.Boolean(required=True),
        "rejected_reason": fields.String(required=True),
        "ip_restriction": fields.Boolean(required=True),
        "password_protection": fields.Boolean(required=True),
        "created_at": fields.DateTime(required=True),
        "updated_at": fields.DateTime(required=True),
        "contacts": fields.List(fields.Nested(ContactModel), required=True),
        "scans": fields.List(fields.String()),
    },
)

ScanResultModel = api.model(
    "ScanResultModel",
    {
        "oid": fields.String(required=True),
        "name": fields.String(required=True),
        "host": fields.String(required=True),
        "port": fields.String(required=True),
        "description": fields.String(required=True),
        "qod": fields.String(required=True),
        "severity": fields.String(required=True),
        "severity_rank": fields.String(required=True),
        "scanner": fields.String(required=True),
        "fix_required": fields.String(required=True),
    },
)

ScanOutputModel = api.model(
    "ScanOutputModel",
    {
        "target": fields.String(required=True),
        "uuid": fields.String(required=True, attribute=lambda scan: scan["uuid"].hex),
        "error_reason": fields.String(required=True),
        "comment": fields.String(required=True),
        "created_at": fields.DateTime(required=True),
        "updated_at": fields.DateTime(required=True),
        "scheduled": fields.Boolean(required=True),
        "processed": fields.Boolean(required=True),
        "start_at": fields.DateTime(required=True),
        "end_at": fields.DateTime(required=True),
        "results": fields.List(fields.Nested(ScanResultModel), required=True),
    },
)


@api.route("/")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(400, "Bad Request")
@api.response(401, "Invalid Token")
class AuditList(AuditResource):

    AuditListGetParser = reqparse.RequestParser()
    AuditListGetParser.add_argument("submitted", type=inputs.boolean, default=False, location="args")
    AuditListGetParser.add_argument("approved", type=inputs.boolean, default=False, location="args")
    AuditListGetParser.add_argument("page", type=int, default=1, location="args")
    AuditListGetParser.add_argument("count", type=int, default=10, location="args")

    AuditListPostInputModel = api.model(
        "AuditListPostInput",
        {
            "name": fields.String(required=True),
            "contacts": fields.List(fields.Nested(ContactModel), required=True),
        },
    )

    @api.expect(AuditListGetParser)
    @api.marshal_with(AuditOutputModel, skip_none=True, as_list=True)
    @Authorizer.admin_token_required
    def get(self):
        """Get audit list"""
        schema = AuditListInputSchema()
        params, errors = schema.load(request.args)
        if errors:
            abort(400, errors)

        audit_query = (
            AuditTable.select(
                AuditTable,
                fn.GROUP_CONCAT(
                    ContactTable.name,
                    ContactSchema.SEPARATER_NAME_EMAIL,
                    ContactTable.email,
                    python_value=(
                        lambda contacts: [
                            dict(zip(["name", "email"], contact.rsplit(ContactSchema.SEPARATER_NAME_EMAIL)))
                            for contact in contacts.split(ContactSchema.SEPARATER_CONTACTS)
                        ]
                    ),
                ).alias("contacts"),
            )
            .where(
                (AuditTable.submitted == params["submitted"]) & (AuditTable.approved == params["approved"])
            )
            .join(ContactTable, on=(AuditTable.id == ContactTable.audit_id))
            .group_by(AuditTable.id)
            .order_by(AuditTable.updated_at.desc())
            .paginate(params["page"], params["count"])
        )

        return list(audit_query.dicts())

    @api.expect(AuditListPostInputModel)
    @api.marshal_with(AuditOutputModel)
    @Authorizer.admin_token_required
    def post(self):
        """Register new audit"""
        schema = AuditInputSchema()
        params, errors = schema.load(request.json)
        if errors:
            abort(400, errors)

        with db.database.atomic():
            audit = AuditTable(**params)
            audit.save()

            for contact in params["contacts"]:
                contact["audit_id"] = audit.id

            ContactTable.insert_many(params["contacts"]).execute()

        return AuditResource.get_by_uuid(audit.uuid, withContacts=True, withScans=True)


@api.route("/<string:audit_uuid>/tokens/")
@api.doc(security="None")
@api.response(200, "Success")
class AuditToken(AuditResource):

    AuditTokenInputModel = api.model("AuditTokenInput", {"password": fields.String()})
    AuditTokenModel = api.model("AuditToken", {"token": fields.String(required=True)})

    @api.expect(AuditTokenInputModel)
    @api.marshal_with(AuditTokenModel)
    @api.response(401, "Invalid Password")
    @api.response(403, "Invalid Source IP")
    @api.response(404, "Not Found")
    def post(self, audit_uuid):
        """Publish an API token for the specified audit"""
        audit = AuditResource.get_by_uuid(audit_uuid, withContacts=False, withScans=False)

        if audit["ip_restriction"] == True:
            if Utils.is_source_ip_permitted(request.access_route[0]) == False:
                abort(403, "Not allowed to access from your IP address")

        if audit["password_protection"] == True:
            params, errors = AuditTokenInputSchema().load(request.json)
            if errors:
                abort(400, errors)

            if Utils.get_password_hash(params["password"]) != audit["password"]:
                abort(401, "Invalid password")

        token = create_access_token(identity={"scope": audit_uuid})
        return {"token": token}, 200


@api.route("/<string:audit_uuid>/")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class AuditItem(AuditResource):

    AuditPatchInputModel = api.model(
        "AuditPatchInput",
        {
            "name": fields.String(),
            "contacts": fields.List(fields.Nested(ContactModel)),
            "ip_restriction": fields.Boolean(),
            "password_protection": fields.Boolean(),
            "password": fields.String(),
        },
    )

    @api.marshal_with(AuditOutputModel)
    @Authorizer.token_required
    def get(self, audit_uuid):
        """Get the specified audit"""
        return AuditResource.get_by_uuid(audit_uuid, withContacts=True, withScans=True)

    @api.expect(AuditPatchInputModel)
    @api.marshal_with(AuditOutputModel)
    @api.response(400, "Bad Request")
    @Authorizer.token_required
    def patch(self, audit_uuid):
        """Update the specified audit"""
        audit = AuditResource.get_by_uuid(audit_uuid, withContacts=False, withScans=False)

        schema = AuditUpdateSchema(
            only=["name", "contacts", "password", "ip_restriction", "password_protection"]
        )
        params, errors = schema.load(request.json)
        if errors:
            abort(400, errors)

        if params.get("password_protection") == True and "password" not in params:
            abort(400, "Password must be provided when enforcing protection")

        if "contacts" in params:
            contacts = params["contacts"]
            params.pop("contacts")

        with db.database.atomic():
            AuditTable.update(params).where(AuditTable.id == audit["id"]).execute()

            if contacts:
                for contact in contacts:
                    contact["audit_id"] = audit["id"]
                ContactTable.delete().where(ContactTable.audit_id == audit["id"]).execute()
                ContactTable.insert_many(contacts).execute()

        return AuditResource.get_by_uuid(audit["uuid"], withContacts=True, withScans=True)

    @Authorizer.admin_token_required
    def delete(self, audit_uuid):
        """Delete the specified audit"""
        audit_query = AuditTable.delete().where(AuditTable.uuid == audit_uuid)
        if audit_query.execute() == 0:
            abort(404, "Not Found")
        else:
            return {}


@api.route("/<string:audit_uuid>/submit/")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class AuditSubmission(AuditResource):

    AuditWithdrawalInputModel = api.model("AuditWithdrawalInput", {"rejected_reason": fields.String()})

    @api.marshal_with(AuditOutputModel)
    @Authorizer.token_required
    def post(self, audit_uuid):
        """Submit the specified audit result"""
        audit = AuditResource.get_by_uuid(audit_uuid, withContacts=False, withScans=False)

        if audit["submitted"] == True:
            abort(400, "Already approved")

        if audit["approved"] == True:
            abort(400, "Already approved by administrator(s)")

        schema = AuditUpdateSchema(only=["submitted", "rejected_reason"])
        params, _errors = schema.load({"submitted": True, "rejected_reason": ""})

        with db.database.atomic():
            AuditTable.update(params).where(AuditTable.id == audit["id"]).execute()

        return AuditResource.get_by_uuid(audit["uuid"], withContacts=True, withScans=True)

    @api.expect(AuditWithdrawalInputModel)
    @api.marshal_with(AuditOutputModel)
    @Authorizer.token_required
    def delete(self, audit_uuid):
        """Withdraw the submission of the specified audit result"""
        audit = AuditResource.get_by_uuid(audit_uuid, withContacts=False, withScans=False)

        if audit["submitted"] == False:
            abort(400, "Not submitted yet")

        if audit["approved"] == True:
            abort(400, "Already approved by administrator(s)")

        schema = AuditUpdateSchema(only=["submitted", "rejected_reason"])
        params, errors = schema.load(
            {"submitted": False, "rejected_reason": ""}  # TODO: Get rejected reason from UI
        )
        if errors:
            abort(400, errors)

        with db.database.atomic():
            AuditTable.update(params).where(AuditTable.id == audit["id"]).execute()

        return AuditResource.get_by_uuid(audit["uuid"], withContacts=True, withScans=True)


@api.route("/<string:audit_uuid>/approve/")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class AuditApproval(AuditResource):
    @api.marshal_with(AuditOutputModel)
    @Authorizer.admin_token_required
    def post(self, audit_uuid):
        """Approve the specified audit submission"""
        audit = AuditResource.get_by_uuid(audit_uuid, withContacts=False, withScans=False)

        if audit["approved"] == True:
            abort(400, "Already approved")

        schema = AuditUpdateSchema(only=["approved", "submitted"])
        params, _errors = schema.load({"approved": True, "submitted": True})

        with db.database.atomic():
            AuditTable.update(params).where(AuditTable.id == audit["id"]).execute()

        return AuditResource.get_by_uuid(audit["uuid"], withContacts=True, withScans=True)

    @api.marshal_with(AuditOutputModel)
    @Authorizer.admin_token_required
    def delete(self, audit_uuid):
        """Withdraw the approval of the specified audit submission"""
        audit = AuditResource.get_by_uuid(audit_uuid, withContacts=False, withScans=False)

        if audit["approved"] == False:
            abort(400, "Not approved yet")

        schema = AuditUpdateSchema(only=["approved"])
        params, _errors = schema.load({"approved": False})

        with db.database.atomic():
            AuditTable.update(params).where(AuditTable.id == audit["id"]).execute()

        return AuditResource.get_by_uuid(audit["uuid"], withContacts=True, withScans=True)


@api.route("/<string:audit_uuid>/download/")
@api.doc(security="API Token")
@api.response(200, "Success", headers={"Content-Type": "text/csv", "Content-Disposition": "attachment"})
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class AuditDownload(AuditResource):

    AUDIT_CSV_COLUMNS = [
        "target",
        "host",
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

    @Authorizer.token_required
    def get(self, audit_uuid):
        """Download the specified audit result"""
        audit_query = AuditTable.select().where(AuditTable.uuid == audit_uuid)

        scan_ids = []
        for scan in audit_query[0].scans.dicts():
            if scan["processed"] is True:
                scan_ids.append(scan["id"])

        results = (
            ResultTable.select(ResultTable, ScanTable, VulnTable)
            .join(ScanTable)
            .join(VulnTable, on=(ResultTable.oid == VulnTable.oid))
            .where(ResultTable.scan_id.in_(scan_ids))
            .order_by(ResultTable.scan_id)
        )

        with tempfile.TemporaryFile("r+") as f:
            writer = csv.DictWriter(f, AuditDownload.AUDIT_CSV_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for result in results.dicts():
                writer.writerow(result)
            f.flush()
            f.seek(0)
            output = f.read()

        headers = {"Content-Type": "text/csv", "Content-Disposition": "attachment"}
        return Response(response=output, status=200, headers=headers)


@api.route("/<string:audit_uuid>/scan/")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class ScanList(ScanResource):

    ScanListPostInputModel = api.model("ScanListPostInput", {"target": fields.String(required=True)})
    ScanListPostErrorResponseModel = api.model(
        "ScanListPostErrorResponse",
        {
            "error_reason": fields.String(
                enum=[
                    "audit-id-not-found",
                    "audit-submitted",
                    "target-is-private-ip",
                    "could-not-resolve-target-fqdn",
                    "target-is-not-fqdn-or-ipv4",
                ],
                required=True,
            )
        },
    )

    @api.expect(ScanListPostInputModel)
    @api.marshal_with(ScanOutputModel)
    @api.response(400, "Bad Request", ScanListPostErrorResponseModel)
    @Authorizer.token_required
    @ScanResource.reject_if_submitted_or_approved
    def post(self, audit_uuid):
        """Register new scan"""
        schema = ScanInputSchema()
        params, errors = schema.load(request.json)
        if errors:
            abort(400, errors)

        audit_id = AuditResource.get_audit_id_by_uuid(audit_uuid)

        scan_insert_query = ScanTable(target=params["target"], audit_id=audit_id)
        scan_insert_query.save()
        return ScanResource.get_by_uuid(scan_insert_query.uuid)


@api.route("/<string:audit_uuid>/scan/<string:scan_uuid>/")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class ScanItem(Resource):

    ScanPatchInputModel = api.model("ScanPatchInput", {"comment": fields.String(required=True)})

    @api.marshal_with(ScanOutputModel)
    @Authorizer.token_required
    def get(self, audit_uuid, scan_uuid):
        """Retrieve the specified scan"""
        return ScanResource.get_by_uuid(scan_uuid, withResults=True)

    @api.expect(ScanPatchInputModel)
    @api.marshal_with(ScanOutputModel)
    @api.response(400, "Bad Request")
    @Authorizer.token_required
    @ScanResource.reject_if_submitted_or_approved
    def patch(self, audit_uuid, scan_uuid):
        """Update the specified scan"""
        scan = ScanResource.get_by_uuid(scan_uuid, withResults=False)
        schema = ScanUpdateSchema(only=["comment"])
        params, errors = schema.load(request.json)
        if errors:
            abort(400, errors)

        ScanTable.update(params).where(ScanTable.id == scan["id"]).execute()
        return ScanResource.get_by_uuid(scan_uuid, withResults=False)

    @Authorizer.token_required
    @ScanResource.reject_if_submitted_or_approved
    def delete(self, audit_uuid, scan_uuid):
        """Delete the specified scan"""
        scan_query = ScanTable.delete().where(ScanTable.uuid == scan_uuid)
        if scan_query.execute() == 0:
            abort(404, "Not Found")
        else:
            return {}


@api.route("/<string:audit_uuid>/scan/<string:scan_uuid>/schedule/")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class ScanSchedule(Resource):

    ScanSchedulePatchInputModel = api.model(
        "ScanSchedulePatchInput",
        {"start_at": fields.DateTime(required=True), "end_at": fields.DateTime(required=True)},
    )

    @api.expect(ScanSchedulePatchInputModel)
    @api.marshal_with(ScanOutputModel)
    @api.response(400, "Bad Request")
    @Authorizer.token_required
    @ScanResource.reject_if_submitted_or_approved
    def patch(self, audit_uuid, scan_uuid):
        """Schedule the specified scan"""
        scan = ScanResource.get_by_uuid(scan_uuid, withResults=False)

        if scan["scheduled"] == True:
            abort(400, "Already scheduled")

        schema = ScanUpdateSchema(only=["start_at", "end_at"])
        params, errors = schema.load(request.json)
        if errors:
            abort(400, errors)

        audit_id = AuditResource.get_audit_id_by_uuid(audit_uuid)

        with db.database.atomic():

            task = PendingTask().add(
                {
                    "audit_id": audit_id,
                    "scan_id": scan["id"],
                    "target": scan["target"],
                    "start_at": params["start_at"],
                    "end_at": params["end_at"],
                }
            )

            params["task_uuid"] = task.uuid
            params["scheduled"] = True
            ScanTable.update(params).where(ScanTable.id == scan["id"]).execute()

        return ScanResource.get_by_uuid(scan_uuid, withResults=False)

    @api.marshal_with(ScanOutputModel)
    @api.response(400, "Bad Request")
    @Authorizer.token_required
    @ScanResource.reject_if_submitted_or_approved
    def delete(self, audit_uuid, scan_uuid):
        """Cancel the specified scan schedule"""
        scan = ScanResource.get_by_uuid(scan_uuid, withResults=False)

        if scan["scheduled"] == False:
            abort(400, "Already canceled")

        data = {
            "start_at": Utils.get_default_datetime(),
            "end_at": Utils.get_default_datetime(),
            "scheduled": False,
            "task_uuid": None,
        }

        ScanTable.update(data).where(ScanTable.id == scan["id"]).execute()
        return ScanResource.get_by_uuid(scan_uuid, withResults=False)
