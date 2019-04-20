from .models import Audit
from .models import Contact
from .models import Result
from .models import Scan
from .models import Vuln
from .models import db


def keep(*module):
    pass


keep(Audit, Contact, Result, Scan, Vuln, db)
