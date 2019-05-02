import os

from flask import current_app as app


class LocalFileStorage:

    RESULT_DIR_NAME = "/results"

    def __init__(self):
        self.results_dir = os.path.realpath(
            os.path.dirname(os.path.abspath(__file__)) + "/.." + self.RESULT_DIR_NAME
        )
        os.makedirs(self.results_dir, exist_ok=True)

    def load(self, key):
        try:
            with open(self.results_dir + "/" + key, "r", encoding="utf8") as file:
                body = file.read()
            return body
        except Exception as e:
            app.logger.error(e)
            return None

    def store(self, key, body):
        try:
            filepath = self.results_dir + "/" + key
            with open(filepath, "w", encoding="utf8") as file:
                file.write(body)
        except Exception as e:
            app.logger.error(e)
            return False

        return True
