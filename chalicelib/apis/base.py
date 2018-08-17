import ipaddress
import logging
import os

logger = logging.getLogger("peewee")
# logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class APIBase:

    RESPONSE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, app):
        self.app = app

    def _get_query_params(self):
        params = self.app.current_request.query_params
        return params if params is not None else {}

    def _get_request_body(self):
        body = self.app.current_request.json_body
        return body if body is not None else {}

    def _is_access_permitted(self):
        try:
            source_ip = self.app.current_request.context["identity"]["sourceIp"]
            permitted_ip_ranges = os.getenv("PERMITTED_IP_ADDRESS_RANGE").split(",")
            source_ip = ipaddress.ip_address(source_ip)

            for permitted_ip_range in permitted_ip_ranges:
                permitted_ip_network = ipaddress.ip_network(permitted_ip_range)
                if source_ip in permitted_ip_network:
                    return True

            return False

        except Exception as e:
            self.app.log.error(e)
            return False
