from flask import request
from flask_restplus import Namespace
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse

from core import Authorizer
from core import PagenationSchema

api = Namespace("vuln")


VulnModel = api.model(
    "Vuln",
    {
        "id": fields.Integer(required=True),
        "oid": fields.String(required=True),
        "fix_required": fields.Boolean(required=True),
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
    VulnListGetParser.add_argument("fix_required", type=inputs.boolean, default=None, location="args")
    VulnListGetParser.add_argument("keyword", type=str, location="args")
    VulnListGetParser.add_argument("page", type=int, default=1, location="args")
    VulnListGetParser.add_argument("count", type=int, default=10, location="args")

    @api.expect(VulnListGetParser, validate=False)
    @api.marshal_with(VulnModel, as_list=True)
    @Authorizer.admin_token_required
    def get(self):
        """Get vulnerability list"""
        pagenation = PagenationSchema()
        pages = pagenation.load(request.args)
        print(pages)
        return []


@api.route("/<string:vuln_id>")
@api.doc(security="API Token")
@api.response(200, "Success")
@api.response(400, "Bad Request")
@api.response(401, "Invalid Token")
@api.response(404, "Not Found")
class Vulnerability(Resource):

    VulnPatchInputModel = api.model("VulnPatchInput", {"fix_required": fields.Boolean(required=True)})

    @api.expect(VulnPatchInputModel, validate=True)
    @Authorizer.admin_token_required
    def patch(self, vuln_id):
        """Decide whether the specified vulnerability requires to be fixed"""
        print(vuln_id)
        return []
