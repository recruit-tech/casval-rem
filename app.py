import os

from chalice import Chalice
from chalice import CORSConfig
from chalicelib import *

app = Chalice(app_name='casval')
app.debug = True

cors_config = CORSConfig(
    allow_origin=os.environ["ORIGIN"],
    allow_headers=['Authorization'],
    max_age=3600,
)


@app.route('/audit', methods=['GET'], cors=cors_config)
def audit_index():
    return audit.index()


@app.route('/audit', methods=['POST'], cors=cors_config)
def audit_post():
    return audit.post()


@app.route('/audit/{audit_id}/tokens', methods=['POST'], cors=cors_config)
def audit_tokens(audit_id):
    return audit.tokens(audit_id)


@app.route('/audit/{audit_id}', methods=['GET'], cors=cors_config)
def audit_get(audit_id):
    return audit.get(audit_id)


@app.route('/audit/{audit_id}', methods=['PATCH'], cors=cors_config)
def audit_patch(audit_id):
    return audit.get(audit_id)


@app.route('/audit/{audit_id}', methods=['DELETE'], cors=cors_config)
def audit_delete(audit_id):
    return audit.delete(audit_id)


@app.route('/audit/{audit_id}/submit', methods=['POST'], cors=cors_config)
def audit_submit(audit_id):
    return audit.submit(audit_id)


@app.route('/audit/{audit_id}/submit', methods=['DELETE'], cors=cors_config)
def audit_submit_cancel(audit_id):
    return audit.submit_cancel(audit_id)


@app.route('/scan', methods=['POST'], cors=cors_config)
def scan_post():
    return scan.post()


@app.route('/scan/{scan_id}', methods=['GET'], cors=cors_config)
def scan_get(scan_id):
    return scan.get(scan_id)


@app.route('/scan/{scan_id}', methods=['PATCH'], cors=cors_config)
def scan_patch(scan_id):
    return scan.patch(scan_id)


@app.route('/scan/{scan_id}', methods=['DELETE'], cors=cors_config)
def scan_delete(scan_id):
    return scan.delete(scan_id)


@app.route('/scan/{scan_id}/schedule', methods=['PATCH'], cors=cors_config)
def scan_schedule(scan_id):
    return scan.schedule(scan_id)


@app.route('/scan/{scan_id}/schedule', methods=['DELETE'], cors=cors_config)
def scan_schedule_cancel(scan_id):
    return scan.schedule_cancel(scan_id)


@app.route('/auth', methods=['POST'], cors=cors_config)
def auth():
    return auth.auth()


@app.route('/vulns', methods=['GET'], cors=cors_config)
def vulnerability_index():
    return vuln.index()


@app.route('/vulns/{oid}', methods=['GET'], cors=cors_config)
def vulnerability_get(oid):
    return vuln.get(oid)


@app.route('/vulns/{oid}', methods=['PATCH'], cors=cors_config)
def vulnerability_get(oid):
    return vuln.patch(oid)
