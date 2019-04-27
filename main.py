import logging
import os

from flask import Flask
from flask_cors import CORS
from peewee import MySQLDatabase

from apis import api
from core import AuditTable
from core import ContactTable
from core import ResultTable
from core import ScanTable
from core import Utils
from core import VulnTable
from core import db
from core import jwt
from core import marshmallow

app = Flask(__name__)

logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


if len(os.getenv("CONFIG_ENV_FILE_PATH", "")) > 0:
    # for production environment
    Utils.load_env_from_config_file(os.environ["CONFIG_ENV_FILE_PATH"])
    app.config["DATABASE"] = MySQLDatabase(
        os.environ["DB_NAME"],
        unix_socket=os.path.join("/cloudsql", os.environ["DB_INSTANCE_NAME"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
else:
    # for development environment
    app.config["DATABASE"] = MySQLDatabase(
        os.getenv("DB_NAME", "casval"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Passw0rd!"),
        host=os.getenv("DB_ENDPOINT", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
    )

app.config["ADMIN_PASSWORD"] = os.getenv("ADMIN_PASSWORD", "admin-password")
app.config["SCANNER"] = os.getenv("SCANNER", "casval-stub")
app.config["PERMITTED_SOURCE_IP_RANGES"] = os.getenv("PERMITTED_SOURCE_IP_RANGES", "")
app.config["PERMITTED_ORIGINS"] = os.getenv("PERMITTED_ORIGINS", "*")
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3 * 3600  # 3 hours
app.config["JWT_IDENTITY_CLAIM"] = "sub"
app.config["RESTPLUS_MASK_SWAGGER"] = False
app.config["SWAGGER_UI_REQUEST_DURATION"] = True
app.config["SWAGGER_UI_DOC_EXPANSION"] = "list"
app.config["SWAGGER_UI_JSONEDITOR"] = True
app.config["TIMEZONE"] = "Asia/Tokyo"
app.config["SCAN_MAX_NUMBER_OF_MESSAGES_IN_QUEUE"] = 10
app.config["SCAN_PENDING_QUEUE_NAME"] = "ScanPending"
app.config["SCAN_RUNNING_QUEUE_NAME"] = "ScanRunning"
app.config["SCAN_STOPPED_QUEUE_NAME"] = "ScanStopped"
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
db.database.create_tables([AuditTable, ContactTable, ScanTable, VulnTable, ResultTable])
jwt.init_app(app)
jwt._set_error_handler_callbacks(api)
marshmallow.init_app(app)
CORS(app, origins=app.config["PERMITTED_ORIGINS"])
