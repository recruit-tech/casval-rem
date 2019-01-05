import os

if os.getenv("SCANNER") == "casval-stub":
    from chalicelib.core.stub import scanner
else:
    from chalicelib.core import scanner

if os.getenv("UNIT_TEST") == "True":
    from chalicelib.core.stub import queues
    from chalicelib.core.stub import storage
else:
    from chalicelib.core import queues
    from chalicelib.core import storage

Scanner = scanner.Scanner
Queue = queues.Queue
Storage = storage.Storage
