import os
from chalicelib.apis.base import APIBase
from chalicelib.core.models import db
from peewee_seed import PeeweeSeed


class TestAPI(APIBase):
    @APIBase.exception_handler
    def __init__(self, app):
        super().__init__(app)
        self._check_stage()

    def post(self):
        body = super()._get_request_body()
        print(body)
        seed = PeeweeSeed(db)
        _, models = seed.load_fixtures([body])
        seed.create_table_all(models)

        seed.db_data_input([body])

        return {"status": "success"}

    def delete(self):
        body = super()._get_request_body()

        seed = PeeweeSeed(db)

        models = body["models"]
        seed.drop_table_all(models)
        return {"status": "success"}

    def _check_stage(self):
        if os.environ["STAGE"] != "dev":
            raise Exception("stage is not dev")
