import os
import api

from chalice import Chalice
from chalice import CORSConfig

app = Chalice(app_name='casval')
app.debug = True

cors_config = CORSConfig(
    allow_origin=os.environ["ORIGIN"],
    allow_headers=['Authorization'],
    max_age=3600,
)


@app.route('/audit', methods=['GET'], cors=cors_config)
def audit_index():
    return api.audit.index()


@app.route('/audit/{audit_id}', methods=['GET'], cors=cors_config)
def audit_get(audit_id):
    return api.audit.get(audit_id)


@app.route('/audit', methods=['POST'], cors=cors_config)
def audit_post():
    return api.audit.post()


@app.route('/audit/{audit_id}', methods=['PATCH'], cors=cors_config)
def audit_patch(audit_id):
    return api.audit.patch(audit_id)


@app.route('/audit/{audit_id}', methods=['DELETE'], cors=cors_config)
def audit_delete(audit_id):
    return api.audit.delete(audit_id)


@app.route('/audit/{audit_id}/tokens', methods=['POST'], cors=cors_config)
def audit_tokens(audit_id):
    return api.audit.tokens(audit_id)


@app.route('/audit/{audit_id}/submit', methods=['POST'], cors=cors_config)
def audit_submit(audit_id):
    return api.audit.submit(audit_id)


@app.route('/audit/{audit_id}/submit', methods=['DELETE'], cors=cors_config)
def audit_submit_cancel(audit_id):
    return api.audit.submit_cancel(audit_id)


@app.route('/scan/{scan_id}', methods=['GET'], cors=cors_config)
def scan_get(scan_id):
    return api.scan.get(scan_id)


@app.route('/scan', methods=['POST'], cors=cors_config)
def scan_post():
    return api.scan.post()


@app.route('/scan/{scan_id}', methods=['PATCH'], cors=cors_config)
def scan_patch(scan_id):
    return api.scan.patch(scan_id)


@app.route('/scan/{scan_id}', methods=['DELETE'], cors=cors_config)
def scan_delete(scan_id):
    return api.scan.delete(scan_id)


@app.route('/scan/{scan_id}/schedule', methods=['PATCH'], cors=cors_config)
def scan_schedule(scan_id):
    return api.scan.schedule(scan_id)


@app.route('/scan/{scan_id}/schedule', methods=['DELETE'], cors=cors_config)
def scan_schedule_cancel(scan_id):
    return api.scan.schedule_cancel(scan_id)


@app.route('/auth', methods=['POST'], cors=cors_config)
def auth():
    return api.auth.auth()


@app.route('/vulns', methods=['GET'], cors=cors_config)
def vulnerability_index():
    return api.vuln.index()


@app.route('/vulns/{oid}', methods=['GET'], cors=cors_config)
def vulnerability_get(oid):
    return api.vuln.get(oid)


@app.route('/vulns/{oid}', methods=['PATCH'], cors=cors_config)
def vulnerability_patch(oid):
    return api.vuln.patch(oid)
