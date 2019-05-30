import os
from enum import Enum
from enum import auto
from xml.etree import ElementTree

from flask import current_app as app

from core.manager import KubernetesManager as Manager
from core.manager import ManagerStatus
from openvas_lib import VulnscanManager
from openvas_lib import report_parser_from_text


class ScanStatus(Enum):
    RUNNING = auto()
    STOPPED = auto()
    FAILED = auto()


class OpenVASScanner:

    SCANNER_NAME = "OpenVAS Default"
    DEFAULT_TIMEOUT = 60

    def __init__(self, session=None):

        self.host = None
        self.port = int(os.getenv("OPENVAS_MANAGER_PORT", "9390"))
        self.user = os.getenv("OPENVAS_USERNAME", "admin")
        self.password = os.getenv("OPENVAS_PASSWORD", "admin")
        self.profile = os.getenv("OPENVAS_PROFILE", "Full and very deep")
        self.alive_test = os.getenv("OPENVAS_ALIVE_TEST", "Consider Alive")
        self.manager_id = None

        if session != None:
            self.session = session
            self.host = session["blob"].get("openvas_host")
            self.port = session["blob"].get("openvas_port")
            self.manager_id = session["blob"].get("openvas_manager_id")
            if session.get("status") == "CREATED":
                self.conn = self._connect()

        return

    def launch_scan(self, target):
        try:
            app.logger.info("[Scanner] Trying to launch new scan session...")
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
                    "openvas_manager_id": self.manager_id,
                },
            }

            app.logger.info("[Scanner] Launched, session={}".format(session))
            return session

        except Exception as error:
            app.logger.error(error)
            return None

    def check_status(self):
        try:
            status = self.conn.get_scan_status(self.session["blob"]["openvas_scan_id"])

            app.logger.info("[Scanner] current status={}, session={}".format(status, self.session))

            # https://github.com/greenbone/gvmd/blob/577f1b463f5861794bb97066dd0c9c4ab6c223df/src/manage.c#L1482
            # const char*
            # run_status_name (task_status_t status)
            # {
            #   switch (status)
            #     {
            #       case TASK_STATUS_DELETE_REQUESTED:
            #       case TASK_STATUS_DELETE_WAITING:
            #         return "Delete Requested";
            #       case TASK_STATUS_DELETE_ULTIMATE_REQUESTED:
            #       case TASK_STATUS_DELETE_ULTIMATE_WAITING:
            #         return "Ultimate Delete Requested";
            #       case TASK_STATUS_DONE:             return "Done";
            #       case TASK_STATUS_NEW:              return "New";
            #
            #       case TASK_STATUS_REQUESTED:        return "Requested";
            #
            #       case TASK_STATUS_RUNNING:          return "Running";
            #
            #       case TASK_STATUS_STOP_REQUESTED_GIVEUP:
            #       case TASK_STATUS_STOP_REQUESTED:
            #       case TASK_STATUS_STOP_WAITING:
            #         return "Stop Requested";
            #
            #       case TASK_STATUS_STOPPED:          return "Stopped";
            #       default:                           return "Interrupted";
            #     }
            # }

            if status in ["New", "Running", "Requested"]:
                return ScanStatus.RUNNING
            elif status in ["Done"]:
                return ScanStatus.STOPPED
            else:
                return ScanStatus.FAILED
        except Exception as error:
            app.logger.error(error)
            return ScanStatus.RUNNING

    def create(self):
        if os.getenv("OPENVAS_MANAGER_ENDPOINT") is not None:
            session = {
                "status": "CREATED",
                "blob": {
                    "openvas_host": os.getenv("OPENVAS_MANAGER_ENDPOINT"),
                    "openvas_port": int(os.getenv("OPENVAS_MANAGER_PORT", "9390")),
                    "openvas_manager_id": "nothing",
                },
            }
            return session

        manager = Manager()
        if self.manager_id is None:
            manager_status = manager.create(container_image="mikesplain/openvas:9", container_port=9390)
        else:
            manager_status = manager.create(
                uuid=self.manager_id, container_image="mikesplain/openvas:9", container_port=9390
            )

        session = {"status": "", "blob": {"openvas_manager_id": manager_status["uuid"]}}
        if manager_status["status"] == ManagerStatus.RUNNING:
            session["blob"]["openvas_host"] = manager_status["ip"]
            session["blob"]["openvas_port"] = manager_status["port"]
            session["status"] = "CREATED"
        elif manager_status["status"] == ManagerStatus.WAITING:
            session["status"] = "WAITING"
        elif manager_status["status"] == ManagerStatus.FAILED:
            session["status"] = "FAILED"
        elif manager_status["status"] == ManagerStatus.NOT_EXSIT:
            session["status"] = "FAILED"

        return session

    def delete(self):
        if os.getenv("OPENVAS_MANAGER_ENDPOINT") is None:
            manager = Manager()
            manager.delete(self.manager_id)

        self.conn.delete_scan(self.session["blob"]["openvas_scan_id"])
        self.conn.delete_target(self.session["blob"]["openvas_target_id"])

    def terminate_scan(self):
        try:
            app.logger.info("[Scanner] Trying to terminate scan session...")

            self.conn.delete_scan(self.session["blob"]["openvas_scan_id"])
            self.conn.delete_target(self.session["blob"]["openvas_target_id"])

            app.logger.info("[Scanner] Terminated.")
            return True
        except Exception as error:
            app.logger.error(error)
            return False

    def get_report(self):
        try:
            app.logger.info("[Scanner] Trying to get report...")

            ov_report_id = self.conn.get_report_id(self.session["blob"]["openvas_scan_id"])

            app.logger.info("[Scanner] Found report_id={}".format(ov_report_id))

            report_xml = self.conn.get_report_xml(ov_report_id)
            report_txt = ElementTree.tostring(report_xml, encoding="unicode", method="xml")
            app.logger.info("[Scanner] Report downloaded, {} characters.".format(len(report_txt)))
            self.conn.delete_report(ov_report_id)
            return report_txt
        except Exception as error:
            app.logger.error(error)
            return None

    def _connect(self):
        app.logger.info("[Scanner] Trying to connect to {}:{} ...".format(self.host, self.port))

        return VulnscanManager(self.host, self.user, self.password, self.port, self.DEFAULT_TIMEOUT)
        # return VulnscanManager("35.221.80.249", "admin", "admin", 443, self.DEFAULT_TIMEOUT)

    @classmethod
    def get_info(cls):
        return {"source_ip": os.getenv("OPENVAS_SCAN_ENDPOINT", "127.0.0.1")}

    @classmethod
    def parse_report(cls, report_txt):
        try:
            app.logger.info("[Scanner] Trying to parse report...")
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
        except Exception as error:
            app.logger.error(error)
            return None
