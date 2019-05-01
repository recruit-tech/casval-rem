import os
from enum import Enum
from enum import auto
from xml.etree import ElementTree

from flask import abort
from flask import current_app as app

from openvas_lib import VulnscanManager
from openvas_lib import report_parser_from_text

DEFAULT_TIMEOUT = 60


class ScanStatus(Enum):
    RUNNING = auto()
    STOPPED = auto()
    FAILED = auto()


class ScannerUtils:
    @staticmethod
    def connect(host, port):
        app.logger.info("Scanner: trying to connect to scanner {}:{} ...".format(host, port))

        return VulnscanManager(
            host,
            os.getenv("OPENVAS_USERNAME", "admin"),
            os.getenv("OPENVAS_PASSWORD", "admin"),
            port,
            DEFAULT_TIMEOUT,
        )


class Scanner:
    @staticmethod
    def launch(target):
        host = os.getenv("OPENVAS_ENDPOINT", "127.0.0.1")
        port = int(os.getenv("OPENVAS_PORT", "9390"))
        # FIXME
        # profile = os.getenv("OPENVAS_PROFILE", "Full and fast")
        profile = os.getenv("OPENVAS_PROFILE", "Discovery")
        try:
            app.logger.info("Scanner: try to launch new scan session...")

            conn = ScannerUtils.connect(host, port)
            openvas_scan_id, openvas_target_id = conn.launch_scan(target=target, profile=profile)
            session = {
                "openvas_host": host,
                "openvas_port": port,
                "openvas_profile": profile,
                "openvas_scan_id": openvas_scan_id,
                "openvas_target_id": openvas_target_id,
            }

            app.logger.info("Scanner: scan session launched: {}".format(session))

            return session

        except Exception as e:
            app.logger.error(e)
            abort(500, "Failed to launch new scan session")

    @staticmethod
    def check_status(session):
        try:
            conn = ScannerUtils.connect(session["openvas_host"], session["openvas_port"])
            status = conn.get_scan_status(session["openvas_scan_id"])

            app.logger.info(
                "Scanner: scan status({scan_id}): {status}".format(
                    scan_id=session["openvas_scan_id"], status=status
                )
            )

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
                result = ScanStatus.RUNNING
            elif status in ["Done"]:
                result = ScanStatus.STOPPED
            else:
                result = ScanStatus.FAILED
            return result
        except Exception as e:
            app.logger.error(e)
            return ScanStatus.RUNNING

    @staticmethod
    def terminate(session):
        try:
            app.logger.info("Scanner: trying to terminate scan session...")

            conn = ScannerUtils.connect(session["openvas_host"], session["openvas_port"])
            conn.delete_scan(session["openvas_scan_id"])
            conn.delete_target(session["openvas_target_id"])

            app.logger.info("Scanner: scan terminated")

            return True
        except Exception as e:
            app.logger.error(e)
            abort(500, "Failed to terminate scan")

    @staticmethod
    def get_report(session):
        try:
            app.logger.info(
                "Scanner: trying to get report of scan_id={}...".format(session["openvas_scan_id"])
            )

            conn = ScannerUtils.connect(session["openvas_host"], session["openvas_port"])
            openvas_report_id = conn.get_report_id(session["openvas_scan_id"])

            app.logger.info("Scanner: report_id found, {}".format(openvas_report_id))

            report_xml = conn.get_report_xml(openvas_report_id)
            report_txt = ElementTree.tostring(report_xml, encoding="unicode", method="xml")
            app.logger.info("Scanner: report retrieved: {size}byte".format(size=len(report_txt)))
            # FIXME
            # conn.delete_report(openvas_report_id)
            return report_txt
        except Exception as e:
            app.logger.error(e)
            abort(500, "Failed to get report")

    @staticmethod
    def parse_report(report_txt):
        try:
            app.logger.debug("Scanner: trying to parse report...")
            parse_records = report_parser_from_text(report_txt, ignore_log_info=False)
            vulns = []
            results = []

            for record in parse_records:
                vuln = {
                    "oid": record.nvt.oid,
                    "name": record.nvt.name,
                    "cvss_base": record.nvt.cvss_base,
                    "cve": ",".join(record.nvt.cve),
                    "description": record.nvt.tags[0],
                }
                vulns.append(vuln)

                result = {
                    "name": record.host,
                    "port": record.port.port_name,
                    "vuln_id": vuln["oid"],
                    "description": vuln["description"],
                    "qod": "",
                    "severity": "",
                    "severity_rank": record.threat,
                    "scanner": "",
                }
                results.append(result)

            return {"results": results, "vulns": vulns}
        except Exception as e:
            app.logger.error(e)
            abort(500, "Failed to parse report")
