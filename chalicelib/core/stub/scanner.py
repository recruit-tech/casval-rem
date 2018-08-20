class Scanner:
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
        return [
            {
                "@id": "60c9d423-509e-43e8-9bba-ad66e61cd7ff",
                "name": "Apache Web Server Detection",
                "owner": {"name": "admin"},
                "comment": None,
                "creation_time": "2018-08-13T22:40:45Z",
                "modification_time": "2018-08-13T22:40:45Z",
                "user_tags": {"count": "0"},
                "host": {
                    "asset": {"@asset_id": "589af578-3361-4223-a585-f84a333344e2"},
                    "#text": "153.120.5.32",
                },
                "port": "8080/tcp",
                "nvt": {
                    "@oid": "1.3.6.1.4.1.25623.1.0.900498",
                    "type": "nvt",
                    "name": "Apache Web Server Detection",
                    "family": "Product detection",
                    "cvss_base": "0.0",
                    "cve": "NOCVE",
                    "bid": "NOBID",
                    "xref": "NOXREF",
                    "tags": "cvss_base_vector=AV:N/AC:L/Au:N/C:N/I:N/A:N|summary=Detects the installed version of Apache Web Server\n\n  The script detects the version of Apache HTTP Server on remote host and sets the KB.|qod_type=remote_banner",
                    "cert": None,
                },
                "scan_nvt_version": "$Revision: 10290 $",
                "threat": "Log",
                "severity": "0.0",
                "qod": {"value": "80", "type": "remote_banner"},
                "description": "Detected Apache\n\nVersion:  unknown\nLocation: 8080/tcp\nCPE: cpe:/a:apache:http_server",
            },
            {
                "@id": "c15a893f-70dd-46b8-ac40-67d3f07a87aa",
                "name": "CPE Inventory",
                "owner": {"name": "admin"},
                "comment": None,
                "creation_time": "2018-08-13T22:46:22Z",
                "modification_time": "2018-08-13T22:46:22Z",
                "user_tags": {"count": "0"},
                "host": {
                    "asset": {"@asset_id": "589af578-3361-4223-a585-f84a333344e2"},
                    "#text": "153.120.5.32",
                },
                "port": "general/CPE-T",
                "nvt": {
                    "@oid": "1.3.6.1.4.1.25623.1.0.810002",
                    "type": "nvt",
                    "name": "CPE Inventory",
                    "family": "Service detection",
                    "cvss_base": "0.0",
                    "cve": "NOCVE",
                    "bid": "NOBID",
                    "xref": "NOXREF",
                    "tags": "cvss_base_vector=AV:N/AC:L/Au:N/C:N/I:N/A:N|summary=This routine uses information collected by other routines about\n  CPE identities (http://cpe.mitre.org/) of operating systems, services and\n  applications detected during the scan.|qod_type=remote_banner",
                    "cert": None,
                },
                "scan_nvt_version": "$Revision: 8140 $",
                "threat": "Log",
                "severity": "0.0",
                "qod": {"value": "80", "type": "remote_banner"},
                "description": "153.120.5.32|cpe:/a:apache:http_server\n153.120.5.32|cpe:/a:dovecot:dovecot\n153.120.5.32|cpe:/a:openbsd:openssh:6.6.1p1\n153.120.5.32|cpe:/o:canonical:ubuntu_linux:14.04",
            },
        ]
