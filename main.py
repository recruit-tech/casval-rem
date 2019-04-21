import os

from flask import Flask
from peewee import MySQLDatabase

from apis import api
from core import Audit
from core import Contact
from core import Result
from core import Scan
from core import Vuln
from core import db
from core import jwt

app = Flask(__name__)

if len(os.getenv("FLASK_CONFIG_JSON_FILE", "")) > 0:
    # for production environment
    app.config["AUDIT_REPORT_BUCKET_NAME"] = ""
    app.config.from_json(os.environ["FLASK_CONFIG_JSON_FILE"], silent=True)
    app.config["DATABASE"] = MySQLDatabase(
        app.config["DB_NAME"]["value"],
        unix_socket=os.path.join("/cloudsql", app.config["DB_INSTANCE_NAME"]["value"]),
        user=app.config["DB_USER"]["value"],
        password=app.config["DB_PASSWORD"]["value"],
    )
else:
    # for development environment
    app.config["AUDIT_REPORT_BUCKET_NAME"] = ""
    app.config["DATABASE"] = MySQLDatabase(
        os.getenv("DB_NAME", "casval"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Passw0rd!"),
        host=os.getenv("DB_ENDPOINT", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
    )

app.config["SCANNER"] = os.getenv("SCANNER", "casval-stub")
app.config["PERMITTED_IP_ADDRESS_RANGE"] = os.getenv("PERMITTED_IP_ADDRESS_RANGE", "127.0.0.0/8")
app.config["PASSWORD_SALT"] = os.getenv("PASSWORD_SALT", "")
app.config["PASSWORD_ITERATION"] = 1000
app.config["PASSWORD_HASH_ALG"] = "sha256"
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3 * 3600  # 3 hours
app.config["JWT_IDENTITY_CLAIM"] = "sub"
app.config["ADMIN_PASSWORD_HASH"] = "1f1eb4713b3d5e9ede7848207152b52fd6ed763f9818856d121dcdd6bf31c4f1"
app.config["RESTPLUS_MASK_SWAGGER"] = False
app.config["SWAGGER_UI_REQUEST_DURATION"] = True
app.config["SWAGGER_UI_DOC_EXPANSION"] = "list"
app.config["SWAGGER_UI_JSONEDITOR"] = True
app.config["TIMEZONE"] = "Asia/Tokyo"
app.config["DATETIME_FORMAT"] = "%Y-%m-%d %H:%M:%S"
app.config["SCAN_MAX_NUMBER_OF_MESSAGES_IN_QUEUE"] = 10
app.config["SCAN_PENDING_QUEUE_NAME"] = "ScanPending"
app.config["SCAN_RUNNING_QUEUE_NAME"] = "ScanRunning"
app.config["SCAN_STOPPED_QUEUE_NAME"] = "ScanStopped"
app.config["SCAN_MAX_COMMENT_LENGTH"] = 1000
app.config["SCAN_MIN_DURATION_IN_SECONDS"] = 2
app.config["SCAN_SCHEDULABLE_DAYS_FROM_NOW"] = 10
app.config["SCAN_SCHEDULABLE_DAYS_FROM_START_DATE"] = 5
app.config["SCAN_MAX_PARALLEL_SESSION"] = 2
app.config["AUDIT_REPORT_BUCKET_KEY"] = "report/{audit_id}/{scan_id}"
app.config["AUDIT_GET_DEFAULT_COUNT"] = 30
app.config["AUDIT_LIST_MAX_COUNT"] = 300
app.config["AUDIT_DOWNLOAD_COLUMNS"] = [
    "target",
    "port",
    "name",
    "cve",
    "cvss_base",
    "severity_rank",
    "fix_required",
    "description",
    "oid",
    "created_at",
    "comment",
]

api.init_app(app)
db.init_app(app)
db.database.create_tables([Audit, Contact, Scan, Vuln, Result])
jwt.init_app(app)
jwt._set_error_handler_callbacks(api)
