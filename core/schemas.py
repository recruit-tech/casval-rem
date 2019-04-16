from flask_restplus import fields
from flask_restplus import reqparse

api = Namespace("audit")

ContactModel = api.model(
    "Contact", {"name": fields.String(required=True), "email": fields.String(required=True)}
)

AuditModel = api.model(
    "Audit",
    {
        "id": fields.Integer(required=False),
        "uuid": fields.String(required=True),
        "name": fields.String(required=True),
        "submitted": fields.Boolean(required=True),
        "rejected_reason": fields.String(required=True),
        "ip_restriction": fields.Boolean(required=True),
        "password_protection": fields.Boolean(required=True),
        "created_at": fields.DateTime(required=True),
        "updated_at": fields.DateTime(required=True),
        "contacts": fields.List(fields.Nested(ContactModel)),
    },
)


@api.route("/")
class AuditList(Resource):

    AuditListQueryParser = reqparse.RequestParser()
    AuditListQueryParser.add_argument(
        "mode",
        type=str,
        default="unsubmitted",
        choices=("unsubmitted", "submitted"),
        location="args",
        required=False,
    )
    AuditListQueryParser.add_argument("page", type=int, default=1, location="args", required=False)
    AuditListQueryParser.add_argument("count", type=int, default=30, location="args", required=False)

    @api.doc(security=None)
    @api.expect(AuditListQueryParser, validate=True)
    @api.marshal_with([AuditModel], description="Audit List")
    @api.response(400, "Bad Request")
    @api.response(401, "Invalid Password")
    def get(self):
        """Retrieve audit list"""
        post_data = request.json
        print(post_data)
        return None

    @api.doc(security=None)
    @api.expect(AuditModel, validate=True)
    @api.marshal_with(AuditModel, description="Registered Audit")
    @api.response(400, "Bad Request")
    @api.response(401, "Invalid Password")
    def post(self):
        """Register new audit"""
        post_data = request.json
        print(post_data)
        return None
