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
from core import AuditTable
from core import AuditTokenInputSchema
from core import AuditUpdateSchema
from core import Authorizer
from core import ContactSchema
from core import ContactTable
from core import ResultTable
from core import ScanTable
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
        "scans": fields.List(fields.String(), required=True),
    },
)

ScanResultModel = api.model(
    "ScanResultModel",
    {
        "id": fields.Integer(required=True),
        "scan_id": fields.Integer(required=True),
        "name": fields.String(required=True),
        "port": fields.String(required=True),
        "vuln_id": fields.String(required=True),
        "description": fields.String(required=True),
        "qod": fields.String(required=True),
        "severity": fields.String(required=True),
        "severity_rank": fields.String(required=True),
        "scanner": fields.String(required=True),
        "fix_required": fields.Boolean(required=True),
    },
)

ScanStatusModel = api.model(
    "ScanStatusModel",
    {"scheduled": fields.Boolean(required=True), "processed": fields.Boolean(required=True)},
)

ScanScheduleModel = api.model(
    "ScanScheduleModel",
    {"start_at": fields.DateTime(required=True), "end_at": fields.DateTime(required=True)},
)

ScanOutputModel = api.model(
    "ScanOutputModel",
    {
        "target": fields.String(required=True),
        "uuid": fields.String(required=True),
        "error_reason": fields.String(required=True),
        "platform": fields.String(required=True),
        "comment": fields.String(required=True),
        "created_at": fields.DateTime(required=True),
        "updated_at": fields.DateTime(required=True),
        "status": fields.Nested(ScanStatusModel, required=True),
        "schedule": fields.Nested(ScanScheduleModel, required=True),
        "results": fields.List(fields.Nested(ScanResultModel), required=True),
    },
)


@api.route("/")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(400, "Bad Request")
@api.response(401, "Invalid Token")
class AuditList(Resource):

    AuditListGetParser = reqparse.RequestParser()
    AuditListGetParser.add_argument("submitted", type=inputs.boolean, default=False, location="args")
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
    @api.marshal_with(AuditOutputModel, as_list=True)
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
            .where(AuditTable.submitted == params["submitted"])
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

        return AuditItem.get_by_uuid(audit.uuid)


@api.route("/<string:audit_uuid>/tokens")
@api.doc(security="None")
@api.response(200, "Success")
class AuditToken(Resource):

    AuditTokenInputModel = api.model("AuditTokenInput", {"password": fields.String()})

    AuditTokenModel = api.model("AuditToken", {"token": fields.String(required=True)})

    @api.expect(AuditTokenInputModel)
    @api.marshal_with(AuditTokenModel)
    @api.response(401, "Invalid Password")
    @api.response(403, "Invalid Source IP")
    @api.response(404, "Not Found")
    def post(self, audit_uuid):
        """Publish an API token for the specified audit"""
        audit = AuditItem.get_by_uuid(audit_uuid)

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


@api.route("/<string:audit_uuid>")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class AuditItem(Resource):

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
        return AuditItem.get_by_uuid(audit_uuid)

    @api.expect(AuditPatchInputModel)
    @api.marshal_with(AuditOutputModel)
    @api.response(400, "Bad Request")
    @Authorizer.token_required
    def patch(self, audit_uuid):
        """Update the specified audit"""
        audit = AuditItem.get_by_uuid(audit_uuid)

        schema = AuditUpdateSchema(
            only=("name", "contacts", "password", "ip_restriction", "password_protection")
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

        return AuditItem.get_by_uuid(audit["uuid"])

    @Authorizer.admin_token_required
    def delete(self, audit_uuid):
        """Delete the specified audit"""
        audit_query = AuditTable.delete().where(AuditTable.uuid == audit_uuid)
        if audit_query.execute() == 0:
            abort(404, "Not Found")
        else:
            return {}

    @staticmethod
    def get_by_uuid(audit_uuid):
        audit_query = AuditTable.select().where(AuditTable.uuid == audit_uuid)

        try:
            audit = audit_query.dicts()[0]
        except:
            abort(404, "Not Found")

        audit["contacts"] = []
        for contact in audit_query[0].contacts.dicts():
            audit["contacts"].append(contact)

        audit["scans"] = []
        for scan in audit_query[0].scans.dicts():
            audit["scans"].append(scan["uuid"].hex)

        return audit


@api.route("/<string:audit_uuid>/submit")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class AuditSubmission(Resource):

    AuditWithdrawalInputModel = api.model("AuditWithdrawalInput", {"rejected_reason": fields.String()})

    @api.marshal_with(AuditOutputModel)
    @Authorizer.token_required
    def post(self, audit_uuid):
        """Submit the specified audit result"""
        audit = AuditItem.get_by_uuid(audit_uuid)
        schema = AuditUpdateSchema(only=("submitted", "rejected_reason"))
        params, _errors = schema.load({"submitted": True, "rejected_reason": ""})

        with db.database.atomic():
            AuditTable.update(params).where(AuditTable.id == audit["id"]).execute()

        return AuditItem.get_by_uuid(audit["uuid"])

    @api.expect(AuditWithdrawalInputModel)
    @api.marshal_with(AuditOutputModel)
    @Authorizer.token_required
    def delete(self, audit_uuid):
        """Withdraw the submission of the specified audit result"""
        audit = AuditItem.get_by_uuid(audit_uuid)
        schema = AuditUpdateSchema(only=("submitted", "rejected_reason"))
        params, errors = schema.load(
            {"submitted": False, "rejected_reason": request.json.get("rejected_reason", "")}
        )
        if errors:
            abort(400, errors)

        with db.database.atomic():
            AuditTable.update(params).where(AuditTable.id == audit["id"]).execute()

        return AuditItem.get_by_uuid(audit["uuid"])


@api.route("/<string:audit_uuid>/download")
@api.doc(security="API Token")
@api.response(200, "Success", headers={"Content-Type": "text/csv", "Content-Disposition": "attachment"})
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class AuditDownload(Resource):

    AUDIT_CSV_COLUMNS = [
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
            .join(VulnTable, on=(ResultTable.vuln_id == VulnTable.oid))
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


@api.route("/<string:audit_uuid>/scan")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class ScanList(Resource):

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
    def post(self, audit_uuid):
        """Register new scan"""
        print(audit_uuid)
        return {}


@api.route("/<string:audit_uuid>/scan/<string:scan_uuid>")
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
        print(audit_uuid)
        return {}

    @api.expect(ScanPatchInputModel)
    @api.marshal_with(ScanOutputModel)
    @api.response(400, "Bad Request")
    @Authorizer.token_required
    def patch(self, audit_uuid, scan_uuid):
        """Update the specified scan"""
        print(audit_uuid)
        return {}

    @Authorizer.token_required
    def delete(self, audit_uuid, scan_uuid):
        """Delete the specified scan"""
        print(audit_uuid)
        return None


@api.route("/<string:audit_uuid>/scan/<string:scan_uuid>/schedule")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class ScanSchedule(Resource):

    ScanSchedulePatchInputModel = api.model(
        "ScanSchedulePatchInput", {"schedule": fields.Nested(ScanScheduleModel, required=True)}
    )

    @api.expect(ScanSchedulePatchInputModel)
    @api.marshal_with(ScanOutputModel)
    @api.response(400, "Bad Request")
    @Authorizer.token_required
    def patch(self, audit_uuid, scan_uuid):
        """Schedule the specified scan"""
        print(audit_uuid)
        return {}

    @Authorizer.token_required
    def delete(self, audit_uuid, scan_uuid):
        """Cancel the specified scan schedule"""
        print(audit_uuid)
        return None
