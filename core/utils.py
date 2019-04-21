import ipaddress

from flask import current_app as app


class Utils:
    @staticmethod
    def is_source_ip_permitted(source_ip_str):
        if len(app.config["PERMITTED_SOURCE_IP_RANGES"]) == 0:
            return True

        permitted_ip_ranges = app.config["PERMITTED_SOURCE_IP_RANGES"].split(",")
        source_ip = ipaddress.ip_address(source_ip_str)

        for permitted_ip_range in permitted_ip_ranges:
            permitted_ip_network = ipaddress.ip_network(permitted_ip_range)
            if source_ip in permitted_ip_network:
                return True

        return False
