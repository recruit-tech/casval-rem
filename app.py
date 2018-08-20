from chalice import Chalice
from chalice import CORSConfig
from chalice import Cron
from chalicelib.apis import AuditAPI
from chalicelib.apis import AuthenticationAPI
from chalicelib.apis import ScanAPI
from chalicelib.apis import vuln
from chalicelib.batches import QueueHandler
from chalicelib.core import authorizer

import os

CASVAL = "casval"

app = Chalice(app_name=CASVAL)
app.debug = True


cors_config = CORSConfig(allow_origin=os.environ["ORIGIN"], allow_headers=["Authorization"], max_age=3600)


@app.authorizer()
def authorize(auth_request):
    return authorizer.authorize(auth_request)


# Audit API


@app.route("/audit", methods=["GET"], cors=cors_config, authorizer=authorize)
def audit_index():
    # For administration users only
    if __authorized_scope() == "*":
        audit_api = AuditAPI(app)
        return audit_api.index()


@app.route("/audit/{audit_uuid}", methods=["GET"], cors=cors_config, authorizer=authorize)
def audit_get(audit_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        audit_api = AuditAPI(app)
        return audit_api.get(audit_uuid)


@app.route("/audit", methods=["POST"], cors=cors_config, authorizer=authorize)
def audit_post():
    # For administration users only
    if __authorized_scope() == "*":
        audit_api = AuditAPI(app)
        return audit_api.post()


@app.route("/audit/{audit_uuid}", methods=["PATCH"], cors=cors_config, authorizer=authorize)
def audit_patch(audit_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        audit_api = AuditAPI(app)
        return audit_api.patch(audit_uuid)


@app.route("/audit/{audit_uuid}", methods=["DELETE"], cors=cors_config, authorizer=authorize)
def audit_delete(audit_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        audit_api = AuditAPI(app)
        return audit_api.delete(audit_uuid)


@app.route("/audit/{audit_uuid}/tokens", methods=["POST"], cors=cors_config)
def audit_tokens(audit_uuid):
    audit_api = AuditAPI(app)
    return audit_api.tokens(audit_uuid)


@app.route("/audit/{audit_uuid}/submit", methods=["POST"], cors=cors_config, authorizer=authorize)
def audit_submit(audit_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        audit_api = AuditAPI(app)
        return audit_api.submit(audit_uuid)


@app.route("/audit/{audit_uuid}/submit", methods=["DELETE"], cors=cors_config, authorizer=authorize)
def audit_submit_cancel(audit_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        audit_api = AuditAPI(app)
        return audit_api.submit_cancel(audit_uuid)


# Scan API


@app.route("/audit/{audit_uuid}/scan/{scan_uuid}", methods=["GET"], cors=cors_config, authorizer=authorize)
def scan_get(audit_uuid, scan_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        scan_api = ScanAPI(app, audit_uuid)
        return scan_api.get(scan_uuid)


@app.route("/audit/{audit_uuid}/scan", methods=["POST"], cors=cors_config, authorizer=authorize)
def scan_post(audit_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        scan_api = ScanAPI(app, audit_uuid)
        return scan_api.post()


@app.route("/audit/{audit_uuid}/scan/{scan_uuid}", methods=["PATCH"], cors=cors_config, authorizer=authorize)
def scan_patch(audit_uuid, scan_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        scan_api = ScanAPI(app, audit_uuid)
        return scan_api.patch(scan_uuid)


@app.route("/audit/{audit_uuid}/scan/{scan_uuid}", methods=["DELETE"], cors=cors_config, authorizer=authorize)
def scan_delete(audit_uuid, scan_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        scan_api = ScanAPI(app, audit_uuid)
        return scan_api.delete(scan_uuid)


@app.route(
    "/audit/{audit_uuid}/scan/{scan_uuid}/schedule", methods=["PATCH"], cors=cors_config, authorizer=authorize
)
def scan_schedule(audit_uuid, scan_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        scan_api = ScanAPI(app, audit_uuid)
        return scan_api.schedule(scan_uuid)


@app.route(
    "/audit/{audit_uuid}/scan/{scan_uuid}/schedule",
    methods=["DELETE"],
    cors=cors_config,
    authorizer=authorize,
)
def scan_schedule_cancel(audit_uuid, scan_uuid):
    if __authorized_scope() in [audit_uuid, "*"]:
        scan_api = ScanAPI(app, audit_uuid)
        return scan_api.schedule_cancel(scan_uuid)


# Authentication API


@app.route("/auth", methods=["POST"], cors=cors_config)
def auth():
    authentication_api = AuthenticationAPI(app)
    return authentication_api.auth()


# Vulnerability API


@app.route("/vulns", methods=["GET"], cors=cors_config, authorizer=authorize)
def vulnerability_index():
    # For administration users only
    if __authorized_scope() == "*":
        return vuln.index()


@app.route("/vulns/{oid}", methods=["GET"], cors=cors_config, authorizer=authorize)
def vulnerability_get(oid):
    # For administration users only
    if __authorized_scope() == "*":
        return vuln.get(oid)


@app.route("/vulns/{oid}", methods=["PATCH"], cors=cors_config, authorizer=authorize)
def vulnerability_patch(oid):
    # For administration users only
    if __authorized_scope() == "*":
        return vuln.patch(oid)


# Batch processes


@app.schedule(Cron("0/10", "*", "*", "*", "?", "*"))
def process_scan_pending_queue(event):
    handler = QueueHandler(app)
    return handler.process_scan_pending_queue()


@app.schedule(Cron("0/10", "*", "*", "*", "?", "*"))
def process_scan_running_queue(event):
    handler = QueueHandler(app)
    return handler.process_scan_running_queue()


@app.schedule(Cron("0/10", "*", "*", "*", "?", "*"))
def process_scan_stopped_queue(event):
    handler = QueueHandler(app)
    return handler.process_scan_stopped_queue()


# For debugging purposes only


@app.route("/handle/pending")
def process_scan_pending_queue_for_debug():
    handler = QueueHandler(app)
    return handler.process_scan_pending_queue()


@app.route("/handle/running")
def process_scan_running_queue_for_debug():
    handler = QueueHandler(app)
    return handler.process_scan_running_queue()


@app.route("/handle/stopped")
def process_scan_stopped_queue_for_debug():
    handler = QueueHandler(app)
    return handler.process_scan_stopped_queue()


# Private functions


def __authorized_scope():
    return app.current_request.context["authorizer"]["scope"]
