import os
from enum import Enum
from enum import auto
from xml.etree import ElementTree

from flask import current_app as app

from core.deployers import DeployerStatus
from openvas_lib import ServerError
from openvas_lib import VulnscanManager
from openvas_lib import report_parser_from_text

from .utils import Utils

if Utils.is_gcp():
    from core.deployers import KubernetesDeployer as Deployer
else:
    from core.deployers import LocalDeployer as Deployer


class ScanStatus(Enum):
    RUNNING = auto()
    STOPPED = auto()
    FAILED = auto()


class OpenVASScanner:

    SCANNER_NAME = "OpenVAS Default"
    OPENVAS_CONTAINER_IMAGE = "mikesplain/openvas:9"
    OPENVAS_CONTAINER_PORT = 9390
    DEFAULT_TIMEOUT = 60

    def __init__(self, session=None):
        self.host = None
        self.port = int(os.getenv("OPENVAS_MANAGER_PORT", "9390"))
        self.user = os.getenv("OPENVAS_USERNAME", "admin")
        self.password = os.getenv("OPENVAS_PASSWORD", "admin")
        self.profile = os.getenv("OPENVAS_PROFILE", "Full and very deep")
        self.alive_test = os.getenv("OPENVAS_ALIVE_TEST", "Consider Alive")
        self.deployer_id = None

        if session:
            # Restore previous scanner session
            self.session = session
            self.host = session["blob"].get("openvas_host")
            self.port = session["blob"].get("openvas_port")
            self.deployer_id = session["blob"].get("openvas_deployer_id")
            if session.get("status") == "CREATED":
                self.conn = self._connect()

    def create(self):
        deployer = Deployer()
        if self.deployer_id is None:
            deployer_status = deployer.create(
                container_image=OPENVAS_CONTAINER_IMAGE, container_port=OPENVAS_CONTAINER_PORT
            )
        else:
            deployer_status = deployer.create(
                uuid=self.deployer_id,
                container_image=OPENVAS_CONTAINER_IMAGE,
                container_port=OPENVAS_CONTAINER_PORT,
            )

        session = {"status": "", "blob": {"openvas_deployer_id": deployer_status["uuid"]}}
        if deployer_status["status"] == DeployerStatus.RUNNING:
            session["blob"]["openvas_host"] = deployer_status["ip"]
            session["blob"]["openvas_port"] = deployer_status["port"]
            session["status"] = "CREATED"
        elif deployer_status["status"] == DeployerStatus.WAITING:
            session["status"] = "WAITING"
        elif deployer_status["status"] == DeployerStatus.FAILED:
            session["status"] = "FAILED"
        elif deployer_status["status"] == DeployerStatus.NOT_EXSIT:
            session["status"] = "FAILED"
        return session

    def delete(self):
        app.logger.info("Trying to delete scanner...")
        if Utils.is_gcp():
            Deployer().delete(self.deployer_id)
        else:
            self.conn.delete_scan(self.session["blob"]["openvas_scan_id"])
            self.conn.delete_target(self.session["blob"]["openvas_target_id"])
        app.logger.info("Completed to delete scanner.")

    def launch_scan(self, target):
        app.logger.info("Trying to launch new scan...")
        ov_scan_id, ov_target_id = self.conn.launch_scan(
            target=target, profile=self.profile, alive_test=self.alive_test
        )
        session = {
            "status": "CREATED",
            "blob": {
                "target": target,
                "openvas_host": self.host,
                "openvas_port": self.port,
                "openvas_profile": self.profile,
                "openvas_scan_id": ov_scan_id,
                "openvas_target_id": ov_target_id,
                "openvas_deployer_id": self.deployer_id,
            },
        }

        app.logger.info("Completed to launch scan, session={}".format(session))
        return session

    def check_status(self):
        try:
            status = self.conn.get_scan_status(self.session["blob"]["openvas_scan_id"])
            app.logger.info("Current scan progress={}, session={}".format(status, self.session))
            # See https://github.com/greenbone/gvmd/blob/577f1b463f5861794bb97066dd0c9c4ab6c223df/src/manage.c#L1482
            if status in ["New", "Running", "Requested"]:
                return ScanStatus.RUNNING
            elif status in ["Done"]:
                return ScanStatus.STOPPED
            else:
                return ScanStatus.FAILED
        except Exception as error:
            app.logger.exception("Scan exception, error={}".format(error))
            return ScanStatus.RUNNING

    def get_report(self):
        app.logger.info("Trying to get scan report...")

        ov_report_id = self.conn.get_report_id(self.session["blob"]["openvas_scan_id"])

        app.logger.info("Found report_id={}".format(ov_report_id))

        report_xml = self.conn.get_report_xml(ov_report_id)
        report_txt = ElementTree.tostring(report_xml, encoding="unicode", method="xml")
        app.logger.info("Completed to downloaded report, {} characters.".format(len(report_txt)))
        self.conn.delete_report(ov_report_id)
        return report_txt

    def _connect(self):
        try:
            app.logger.info("Trying to connect to scanner {}:{} ...".format(self.host, self.port))
            return VulnscanManager(self.host, self.user, self.password, self.port, self.DEFAULT_TIMEOUT)
        except ServerError:
            raise ScanServerException("Scan server connection error.")

    @classmethod
    def get_info(cls):
        return {"source_ip": os.getenv("OPENVAS_SCAN_ENDPOINT", "127.0.0.1")}

    @classmethod
    def parse_report(cls, report_txt):
        app.logger.info("Trying to parse report...")
        parse_records = report_parser_from_text(report_txt, ignore_log_info=False)

        vulns = []
        results = []

        for record in parse_records:
            vuln = {"oid": record.nvt.oid}
            vulns.append(vuln)

            result = {
                "name": record.nvt.name,
                "host": record.host,
                "port": record.port.port_name,
                "cvss_base": record.nvt.cvss_base,
                "cve": ",".join(record.nvt.cve),
                "oid": record.nvt.oid,
                "description": record.nvt.tags[0],
                "qod": "",  # FIXME: not supported by openvas_lib
                "severity": record.severity,
                "severity_rank": record.threat,
                "scanner": OpenVASScanner.SCANNER_NAME,
            }
            results.append(result)

        return {"results": results, "vulns": vulns}


class ScanServerException(Exception):
    pass
