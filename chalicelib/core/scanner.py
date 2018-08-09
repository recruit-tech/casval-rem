class Scanner:
    def __init__(self, name):
        self.name = name

    def launch(self, target):
        self.host = "127.0.0.1"  # ToDo: change
        self.port = 9390  # ToDo: change
        self.id = "ID"  # ToDo: change
        return {"name": self.name, "host": self.host, "port": self.port, "id": self.id}

    def is_completed(self, id):
        return True

    def terminate(self, id):
        return True

    def get_report(self, id):
        return {}

    def parse_report(self, report):
        return {}
