import os
from chalicelib.apis import audit
from chalicelib.apis import scan
from chalicelib.apis import AuthenticationAPI
from chalicelib.apis import vuln
from chalicelib.batches import cron_jobs
from chalicelib.batches import sqs_event_handlers
from chalicelib.core import authorizer
from chalice import Chalice, Cron
from chalice import CORSConfig

SQS_SCAN_COMPLETE = "ScanComplete"

app = Chalice(app_name="casval")
app.debug = True

cors_config = CORSConfig(allow_origin=os.environ["ORIGIN"], allow_headers=["Authorization"], max_age=3600)

# TODO: Distinguish id and uuid in API interfaces

@app.authorizer()
def authorize(auth_request):
    return authorizer.authorize(auth_request)


@app.route("/audit", methods=["GET"], cors=cors_config, authorizer=authorize)
def audit_index():
    # For administration users
    if app.current_request.context["authorizer"]["scope"] == "*":
        return audit.index(app)


@app.route("/audit/{audit_id}", methods=["GET"], cors=cors_config, authorizer=authorize)
def audit_get(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.get(app, audit_id)


@app.route("/audit", methods=["POST"], cors=cors_config, authorizer=authorize)
def audit_post():
    # For administration users
    if app.current_request.context["authorizer"]["scope"] == "*":
        return audit.post(app)


@app.route("/audit/{audit_id}", methods=["PATCH"], cors=cors_config, authorizer=authorize)
def audit_patch(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.patch(app, audit_id)


@app.route("/audit/{audit_id}", methods=["DELETE"], cors=cors_config, authorizer=authorize)
def audit_delete(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.delete(app, audit_id)


@app.route("/audit/{audit_id}/tokens", methods=["POST"], cors=cors_config)
def audit_tokens(audit_id):
    return audit.tokens(app, audit_id)


@app.route("/audit/{audit_id}/submit", methods=["POST"], cors=cors_config, authorizer=authorize)
def audit_submit(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.submit(app, audit_id)


@app.route("/audit/{audit_id}/submit", methods=["DELETE"], cors=cors_config, authorizer=authorize)
def audit_submit_cancel(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.submit_cancel(app, audit_id)


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


@app.route("/auth", methods=["POST"], cors=cors_config)
def authenticate():
    api = AuthenticationAPI(app)
    return api.authenticate()


@app.route("/vulns", methods=["GET"], cors=cors_config, authorizer=authorize)
def vulnerability_index():
    return vuln.index()


@app.route("/vulns/{oid}", methods=["GET"], cors=cors_config, authorizer=authorize)
def vulnerability_get(oid):
    return vuln.get(oid)


@app.route("/vulns/{oid}", methods=["PATCH"], cors=cors_config, authorizer=authorize)
def vulnerability_patch(oid):
    return vuln.patch(oid)


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


# For debugging purposes


@app.route("/batch/launcher")
def scan_launcher_for_debug():
    return cron_jobs.scan_launcher(app)


@app.route("/batch/processor")
def scan_processor_for_debug():
    return cron_jobs.scan_processor(app)
