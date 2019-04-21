from flask import request
from flask_jwt_extended import create_access_token
from flask_restplus import Namespace
from flask_restplus import Resource
from flask_restplus import fields

api = Namespace("auth")


@api.route("/")
class Authenticate(Resource):

    AuthInputModel = api.model("AuthInputModel", {"password": fields.String(required=True)})
    AdminTokenModel = api.model("AdminTokenModel", {"token": fields.String(required=True)})

    @api.doc(security=None)
    @api.expect(AuthInputModel, validate=True)
    @api.marshal_with(AdminTokenModel, description="API Token for Administrators")
    @api.response(200, "Success")
    @api.response(400, "Bad Request")
    @api.response(401, "Invalid Password")
    @api.response(403, "Invalid Source IP")
    def post(self):
        """Publish an API token for administrators"""
        post_data = request.json
        # TODO: Authenticate administrator
        print(post_data)

        token = create_access_token(identity={"scope": "*"})
        return {"token": token}, 200
