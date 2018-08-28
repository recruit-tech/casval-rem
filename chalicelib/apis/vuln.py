from chalicelib.apis.base import APIBase
from chalicelib.core.models import Vuln
from chalicelib.core.validators import PagenationValidator


class VulnAPI(APIBase):
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

        query = Vuln.select(Vuln)

        if params.get("fix_required") == "true":
            query = query.where(Vuln.fix_required == True)  # noqa: E712
        elif params.get("fix_required") == "false":
            query = query.where(Vuln.fix_required == False)  # noqa: E712
        elif params.get("fix_required") == "unknown":
            query = query.where(Vuln.fix_required.is_null())

        if params.get("keyword") != "":
            keyword = params.get("keyword")
            query = query.where((Vuln.oid ** "%{}%".format(keyword)) | (Vuln.name ** "%{}%".format(keyword)))

        query = query.order_by(Vuln.oid.desc())
        query = query.paginate(page, count)

        response = []
        for vulnerability in query.dicts():
            response.append(vulnerability)

        return response

    @APIBase.exception_handler
    def patch(self, _id):
        body = super()._get_request_body()

        if "fix_required" not in body:
            raise Exception("'fix_required': Must be contained.")

        Vuln.update({"fix_required": body["fix_required"]}).where(Vuln.oid == _id).execute()

        return {}
