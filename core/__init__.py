from .authorizers import Authorizer
from .authorizers import jwt
from .models import Audit
from .models import Contact
from .models import Result
from .models import Scan
from .models import Vuln
from .models import db
from .utils import Utils
from .validators import AuthInputSchema
from .validators import ContactSchema
from .validators import PagenationSchema
from .validators import marshmallow


def noop(*args):
    pass


noop(
    Audit,
    Contact,
    Result,
    Scan,
    Vuln,
    db,
    jwt,
    marshmallow,
    Authorizer,
    Utils,
    ContactSchema,
    AuthInputSchema,
    PagenationSchema,
)
