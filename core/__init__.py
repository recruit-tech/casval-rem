from .authorizers import Authorizer
from .authorizers import jwt
from .models import Audit
from .models import Contact
from .models import Result
from .models import Scan
from .models import Vuln
from .models import db
from .utils import Utils


def noop(*args):
    pass


noop(Audit, Contact, Result, Scan, Vuln, db, jwt, Authorizer, Utils)
