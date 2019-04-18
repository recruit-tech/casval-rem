from .models import Audit
from .models import Contact
from .models import Result
from .models import Scan
from .models import Vuln
from .models import db

db.create_tables([Audit, Contact, Scan, Vuln, Result])
