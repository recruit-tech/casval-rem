import os

if os.getenv("SCANNER") == "casval-stub":
    from chalicelib.core.stub import scanner
else:
    from chalicelib.core import scanner

Scanner = scanner.Scanner
