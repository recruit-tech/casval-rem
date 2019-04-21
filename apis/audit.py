from flask import current_app as app
from flask import request
from flask_restplus import Namespace
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse

from core import Audit
from core import admin_token_required
from core import db
from core import token_required

api = Namespace("audit")

ContactModel = api.model(
    "ContactModel", {"name": fields.String(required=True), "email": fields.String(required=True)}
)

AuditModel = api.model(
    "AuditModel",
    {
        "id": fields.Integer(required=True),
        "uuid": fields.String(required=True),
        "name": fields.String(required=True),
        "submitted": fields.Boolean(required=True),
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

ScanModel = api.model(
    "ScanModel",
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

    @api.expect(AuditListGetParser, validate=True)
    @api.marshal_with(AuditModel, as_list=True)
    @admin_token_required
    def get(self):
        """Get audit list"""
        data = request.args.get("count")
        print(data)
        return [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]

    @api.expect(AuditListPostInputModel, validate=True)
    @api.marshal_with(AuditModel)
    @admin_token_required
    def post(self):
        """Register new audit"""
        request.json["name"]

        # TODO: Implement all features
        with db.database.atomic():
            audit = Audit(app=app, name=request.json["name"])
            audit.save()

        return None


@api.route("/<string:audit_uuid>/tokens")
@api.doc(security="None")
@api.response(200, "Success")
class AuditToken(Resource):

    AuditTokenInputModel = api.model("AuditTokenInput", {"password": fields.String()})

    AuditTokenModel = api.model("AuditToken", {"token": fields.String(required=True)})

    @api.expect(AuditTokenInputModel, validate=True)
    @api.marshal_with(AuditTokenModel)
    @api.response(401, "Invalid Password")
    @api.response(403, "Invalid Source IP")
    @api.response(404, "Not Found")
    def post(self, audit_uuid):
        """Publish an API token for the specified audit"""
        print(audit_uuid)
        return {}


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

    @api.marshal_with(AuditModel)
    @token_required
    def get(self, audit_uuid):
        """Get the specified audit"""
        print(audit_uuid)
        return {}

    @api.expect(AuditPatchInputModel, validate=True)
    @api.marshal_with(AuditModel)
    @api.response(400, "Bad Request")
    @token_required
    def patch(self, audit_uuid):
        """Update the specified audit"""
        print(audit_uuid)
        return {}

    @token_required
    def delete(self, audit_uuid):
        """Delete the specified audit"""
        print(audit_uuid)
        return None


@api.route("/<string:audit_uuid>/submit")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class AuditSubmission(Resource):
    @api.marshal_with(AuditModel)
    @token_required
    def post(self, audit_uuid):
        """Submit the specified audit result"""
        print(audit_uuid)
        return {}

    @api.marshal_with(AuditModel)
    @token_required
    def delete(self, audit_uuid):
        """Withdraw the submission of the specified audit result"""
        print(audit_uuid)
        return None


@api.route("/<string:audit_uuid>/download")
@api.doc(security="API Token")
@api.response(200, "Success", headers={"Content-Type": "text/csv", "Content-Disposition": "attachment"})
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class AuditDownload(Resource):
    @token_required
    def get(self, audit_uuid):
        """Download the specified audit result"""
        print(audit_uuid)
        return {}


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

    @api.expect(ScanListPostInputModel, validate=True)
    @api.marshal_with(ScanModel)
    @api.response(400, "Bad Request", ScanListPostErrorResponseModel)
    @token_required
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

    @api.marshal_with(ScanModel)
    @token_required
    def get(self, audit_uuid, scan_uuid):
        """Retrieve the specified scan"""
        print(audit_uuid)
        return {}

    @api.expect(ScanPatchInputModel, validate=True)
    @api.marshal_with(ScanModel)
    @api.response(400, "Bad Request")
    @token_required
    def patch(self, audit_uuid, scan_uuid):
        """Update the specified scan"""
        print(audit_uuid)
        return {}

    @token_required
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

    @api.expect(ScanSchedulePatchInputModel, validate=True)
    @api.marshal_with(ScanModel)
    @api.response(400, "Bad Request")
    @token_required
    def patch(self, audit_uuid, scan_uuid):
        """Schedule the specified scan"""
        print(audit_uuid)
        return {}

    @token_required
    def delete(self, audit_uuid, scan_uuid):
        """Cancel the specified scan schedule"""
        print(audit_uuid)
        return None
