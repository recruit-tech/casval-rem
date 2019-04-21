from .authorizers import admin_token_required
from .authorizers import jwt
from .authorizers import token_required
from .models import Audit
from .models import Contact
from .models import Result
from .models import Scan
from .models import Vuln
from .models import db


def keep(*module):
    pass


keep(Audit, Contact, Result, Scan, Vuln, db, jwt, token_required, admin_token_required)
