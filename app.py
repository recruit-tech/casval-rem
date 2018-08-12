import os
from chalicelib.apis import audit
from chalicelib.apis import scan
from chalicelib.apis import authn
from chalicelib.apis import vuln
from chalicelib.batches import cron_jobs
from chalicelib import authorizer
from chalice import Chalice, Cron
from chalice import CORSConfig

app = Chalice(app_name="casval")
app.debug = True

cors_config = CORSConfig(allow_origin=os.environ["ORIGIN"], allow_headers=["Authorization"], max_age=3600)


@app.authorizer()
def authorize(auth_request):
    return authorizer.authorize(auth_request)


@app.route("/audit", methods=["GET"], cors=cors_config, authorizer=authorize)
def audit_index():
    if app.current_request.context["authorizer"]["scope"] == "*":
        return audit.index(app)


@app.route("/audit/{audit_id}", methods=["GET"], cors=cors_config, authorizer=authorize)
def audit_get(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.get(audit_id)


@app.route("/audit", methods=["POST"], cors=cors_config, authorizer=authorize)
def audit_post():
    # ToDo: Add scope verification
    return audit.post()


@app.route("/audit/{audit_id}", methods=["PATCH"], cors=cors_config, authorizer=authorize)
def audit_patch(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.patch(app, audit_id)


@app.route("/audit/{audit_id}", methods=["DELETE"], cors=cors_config, authorizer=authorize)
def audit_delete(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.delete(audit_id)


@app.route("/audit/{audit_id}/tokens", methods=["POST"], cors=cors_config)
def audit_tokens(audit_id):
    return audit.tokens(audit_id)


@app.route("/audit/{audit_id}/submit", methods=["POST"], cors=cors_config, authorizer=authorize)
def audit_submit(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.submit(audit_id)


@app.route("/audit/{audit_id}/submit", methods=["DELETE"], cors=cors_config, authorizer=authorize)
def audit_submit_cancel(audit_id):
    if app.current_request.context["authorizer"]["scope"] in [audit_id, "*"]:
        return audit.submit_cancel(audit_id)


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
    return authn.authenticate()


@app.route("/vulns", methods=["GET"], cors=cors_config, authorizer=authorize)
def vulnerability_index():
    return vuln.index()


@app.route("/vulns/{oid}", methods=["GET"], cors=cors_config, authorizer=authorize)
def vulnerability_get(oid):
    return vuln.get(oid)


@app.route("/vulns/{oid}", methods=["PATCH"], cors=cors_config, authorizer=authorize)
def vulnerability_patch(oid):
    return vuln.patch(oid)


@app.schedule(Cron("0/1", "*", "*", "*", "?", "*"))
def scan_launcher(event):
    return cron_jobs.scan_launcher(app)


# @app.schedule(Cron('0/3', '*', '*', '*', '?', '*'))
# def scan_processor(event):
#    return cron_jobs.scan_processor(app)


@app.lambda_function(name="scan_launcher_sub_process")
def scan_launcher_sub_process(event, context):
    return cron_jobs.scan_launcher_sub_process(event)


# For debugging purposes


@app.route("/batch/launcher")
def scan_launcher_for_debug():
    return cron_jobs.scan_launcher(app)


@app.route("/batch/processor")
def scan_processor_for_debug():
    return cron_jobs.scan_processor(app)
