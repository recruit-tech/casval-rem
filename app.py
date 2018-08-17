import os

from chalice import Chalice, CORSConfig, Cron

from chalicelib import SQS_SCAN_COMPLETE
from chalicelib.apis import AuditAPI, AuthenticationAPI, scan, vuln
from chalicelib.batches import cron_jobs, sqs_event_handlers
from chalicelib.core import authorizer

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


@app.route("/scan/{scan_id}", methods=["GET"], cors=cors_config, authorizer=authorize)
def scan_get(scan_id):
    return scan.get(scan_id)


@app.route("/scan", methods=["POST"], cors=cors_config, authorizer=authorize)
def scan_post():
    return scan.post()


@app.route("/scan/{scan_id}", methods=["PATCH"], cors=cors_config, authorizer=authorize)
def scan_patch(scan_id):
    return scan.patch(app, scan_id)


@app.route("/scan/{scan_id}", methods=["DELETE"], cors=cors_config, authorizer=authorize)
def scan_delete(scan_id):
    return scan.delete(scan_id)


@app.route("/scan/{scan_id}/schedule", methods=["PATCH"], cors=cors_config, authorizer=authorize)
def scan_schedule(scan_id):
    return scan.schedule(app, scan_id)


@app.route("/scan/{scan_id}/schedule", methods=["DELETE"], cors=cors_config, authorizer=authorize)
def scan_schedule_cancel(scan_id):
    return scan.schedule_cancel(scan_id)


# Authentication API


@app.route("/auth", methods=["POST"], cors=cors_config)
def authenticate():
    authentication_api = AuthenticationAPI(app)
    return authentication_api.authenticate()


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


@app.schedule(Cron("0/30", "*", "*", "*", "?", "*"))
def scan_launcher(event):
    return cron_jobs.scan_launcher(app)


@app.schedule(Cron("0/30", "*", "*", "*", "?", "*"))
def scan_processor(event):
    return cron_jobs.scan_processor(app)


@app.lambda_function(name="async_scan_launch")
def async_scan_launch(event, context):
    return cron_jobs.async_scan_launch(event)


@app.lambda_function(name="async_scan_status_check")
def async_scan_status_check(event, context):
    return cron_jobs.async_scan_status_check(event)


@app.lambda_function(name="async_scan_terminate")
def async_scan_terminate(event, context):
    return cron_jobs.async_scan_terminate(event)


@app.on_sqs_message(queue=SQS_SCAN_COMPLETE)
def scan_completed_handler(event):
    return sqs_event_handlers.scan_completed_handler(event)


# For debugging purposes only


@app.route("/batch/launcher")
def scan_launcher_for_debug():
    return cron_jobs.scan_launcher(app)


@app.route("/batch/processor")
def scan_processor_for_debug():
    return cron_jobs.scan_processor(app)


# Private functions


def __authorized_scope():
    return app.current_request.context["authorizer"]["scope"]
