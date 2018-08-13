import os
import boto3
import json
import logging

from os.path import join, dirname

logger = logging.getLogger()
logger.setLevel(logging.INFO)

OBJECT_KEY_NAME = "report/{scanner}/{scan_id}.{ext}"
REPORT_EXTENSION = "xml"

from chalicelib.core.scanner import Scanner


def scan_completed_handler(messages):
    logger.info(messages)
    try:
        logger.info("try to handle messages in SQS...")
        scanner = Scanner(os.environ["SCANNER"])
        for message in messages:
            logger.info(message)
            body = json.loads(message.body)
            scan_id = body["scan_id"]
            report = load_report(scan_id)
            if report is None:
                logger.info("report not found. try to retrieve from scanner...")
                session = body["session"]
                result = scanner.get_report(session)
                report = result["report"]
                logger.info("report retrieved: {report}".format(report=report))
                result = store_report(scan_id, report)
                logger.info("report stored to s3: {result}".format(result=result))
            logger.info("report: {report}".format(report=report))
            result = scanner.parse_report(report)
            # ToDo: store result to Aurora Serverless
            print(json.dumps(result))
        return True
    except Exception as e:
        logger.error(e)
        raise e


def load_report(scan_id):
    try:
        logger.info(
            "try to load a report of scan {scan_id} ...".format(scan_id=scan_id)
        )
        s3 = boto3.resource("s3")
        key = OBJECT_KEY_NAME.format(
            scanner=os.environ["SCANNER"], scan_id=scan_id, ext=REPORT_EXTENSION
        )
        logger.info("s3 key: {key}".format(key=key))
        bucket_name = get_bucket_name()
        logger.info("s3 bucket name: {bucket}".format(bucket=bucket_name))
        obj = s3.Object(bucket_name, key).get()
        logger.info("s3 object: {obj}".format(obj=obj))
        body = obj["Body"].read()
        return body.decode("utf-8")
    except Exception as e:
        logger.error("error at: load_report")
        logger.info(e)
        return None


def store_report(scan_id, report):
    try:
        logger.info(
            "try to store a report of scan {scan_id} ...".format(scan_id=scan_id)
        )
        s3 = boto3.resource("s3")
        key = OBJECT_KEY_NAME.format(
            scanner=os.environ["SCANNER"], scan_id=scan_id, ext=REPORT_EXTENSION
        )
        bucket_name = get_bucket_name()
        logger.info("s3 bucket name: {bucket}".format(bucket=bucket_name))
        obj = s3.Object(bucket_name, key)
        obj.put(Body=report.encode("utf-8"), ContentEncoding="utf-8")
        return True
    except Exception as e:
        logger.error("error at: store_report")
        logger.info(e)
        return False


def get_bucket_name():
    try:
        tfstate_file_path = join(dirname(__file__), "terraform.tfstate")
        logger.info("tfstate file: {path}".format(path=tfstate_file_path))
        with open(tfstate_file_path, "r") as tfstate_file:
            tfstate = json.load(tfstate_file)
            for module in tfstate["modules"]:
                if "bucket" in module["outputs"]:
                    return module["outputs"]["bucket"]["value"]
    except Exception as e:
        logger.error("error at: get_bucket_name")
        logger.error(e)
        return None
