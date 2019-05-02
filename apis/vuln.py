from flask import abort
from flask import request
from flask_restplus import Namespace
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import reqparse

from core import Authorizer
from core import VulnListInputSchema
from core import VulnTable

api = Namespace("vuln")


VulnOutputModel = api.model(
    "VulnOutput",
    {
        "id": fields.Integer(required=True),
        "oid": fields.String(required=True),
        "fix_required": fields.String(required=True),
        "name": fields.String(required=True),
        "cvss_base": fields.String(required=True),
        "cve": fields.String(required=True),
        "description": fields.String(required=True),
    },
)


@api.route("/")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(400, "Bad Request")
@api.response(401, "Invalid Token")
class VulneravilityList(Resource):

    VulnListGetParser = reqparse.RequestParser()
    VulnListGetParser.add_argument("fix_required", type=str, location="args")
    VulnListGetParser.add_argument("keyword", type=str, location="args")
    VulnListGetParser.add_argument("page", type=int, location="args")
    VulnListGetParser.add_argument("count", type=int, location="args")

    @api.expect(VulnListGetParser)
    @api.marshal_with(VulnOutputModel, as_list=True)
    @Authorizer.admin_token_required
    def get(self):
        """Get vulnerability list"""
        schema = VulnListInputSchema()
        params, errors = schema.load(request.args)
        if errors:
            abort(400, errors)

        vuln_query = VulnTable.select(VulnTable)

        if "fix_required" in params:
            vuln_query = vuln_query.where(VulnTable.fix_required == params["fix_required"])

        if "keyword" in params:
            vuln_query = vuln_query.where(
                (VulnTable.oid ** "%{}%".format(params["keyword"]))
                | (VulnTable.name ** "%{}%".format(params["keyword"]))
            )

        vuln_query = vuln_query.order_by(VulnTable.oid.desc())
        vuln_query = vuln_query.paginate(params["page"], params["count"])

        response = []
        for vulnerability in vuln_query.dicts():
            response.append(vulnerability)

        return response


@api.route("/<string:vuln_id>")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(400, "Bad Request")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class Vulnerability(Resource):

    VulnPatchInputModel = api.model("VulnPatchInput", {"fix_required": fields.String(required=True)})

    @api.expect(VulnPatchInputModel, validate=True)
    @Authorizer.admin_token_required
    def patch(self, vuln_id):
        """Decide whether the specified vulnerability requires to be fixed"""
        print(vuln_id)
        return []
