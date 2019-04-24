from .authorizers import Authorizer
from .authorizers import jwt
from .models import AuditTable
from .models import ContactTable
from .models import ResultTable
from .models import ScanTable
from .models import VulnTable
from .models import db
from .utils import Utils
from .validators import AuthInputSchema
from .validators import ContactSchema
from .validators import VulnListInputSchema
from .validators import marshmallow


def noop(*args):
    pass


noop(
    AuditTable,
    ContactTable,
    ResultTable,
    ScanTable,
    VulnTable,
    db,
    jwt,
    marshmallow,
    Authorizer,
    Utils,
    ContactSchema,
    AuthInputSchema,
    VulnListInputSchema,
)
