import boto3
import json


class Scanner(object):
    def __init__(self, name):
        self.name = name

    def launch(self, target):
        result = self.__invoke("launch", {"target": target})
        if "scan_id" not in result:
            raise Exception(result)
        return result

    def check_status(self, session):
        return self.__invoke("check_status", session)

    def terminate(self, session):
        return self.__invoke("terminate", session)

    def get_report(self, session):
        return self.__invoke("get_report", session)

    def parse_report(self, report):
        return self.__invoke("parse_report", report)

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
