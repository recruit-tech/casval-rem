import boto3
import json


class Scanner:
    def __init__(self, name):
        self.name = name

    def launch(self, target):
        return self.__invoke("launch", {"target": target})

    def is_completed(self, id):
        self.__invoke("is_completed", {"id": id})
        return True

    def terminate(self, session):
        self.__invoke("terminate", {"session": id})
        return True

    def get_report(self, id):
        self.__invoke("get_report", {"id": id})
        return {}

    def parse_report(self, report):
        # ToDo: process report xml
        return {}

    def __invoke(self, func, payload):
        try:
            lmd = boto3.client("lambda")
            response = lmd.invoke(
                FunctionName=self.name + "-" + func,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )
            return json.loads(response["Payload"].read())
        except Exception as e:
            return {"error": str(e)}
