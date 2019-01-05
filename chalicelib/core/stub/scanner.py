class Scanner(object):
    def __init__(self, name):
        self.name = name

    def launch(self, target):
        session = {"host": "127.0.0.1", "port": 9390, "scan_id": "<scan_id>", "target_id": "<target_id>"}
        return session

    def check_status(self, session):
        return "complete"

    def terminate(self, session):
        return {}

    def get_report(self, session):
        return '<report content_type="text/xml"></report>'

    def parse_report(self, report):

        vuln = {}
        vuln["oid"] = "1.3.6.1.4.1.25623.1.0.900498"
        vuln["name"] = "Apache Web Server Detection"
        vuln["cvss_base"] = "0.0"
        vuln["cve"] = "NOCVE"
        vuln["description"] = (
            "cvss_base_vector=AV:N/AC:L/Au:N/C:N/I:N/A:N| "
            "summary=Detects the installed version of Apache "
            "Web Server\n\n "
            "The script detects the version of Apache HTTP Server on remote host and sets the KB.| "
            "qod_type=remote_banner"
        )

        result = {}
        result["name"] = "Apache Web Server Detection"
        result["port"] = "general/CPE-T"
        result["vuln_id"] = ""
        result["description"] = (
            "153.120.5.32|cpe:/a:apache:http_server\n153.120.5.32|"
            "cpe:/a:dovecot:dovecot\n153.120.5.32|"
            "cpe:/a:openbsd:openssh:6.6.1p1\n153.120.5.32|"
            "cpe:/o:canonical:ubuntu_linux:14.04"
        )

        result["qod"] = {"value": "80", "type": "remote_banner"}
        result["severity"] = "0.0"
        result["severity_rank"] = ""
        result["scanner"] = ""

        return {"results": [result], "vulns": [vuln]}
