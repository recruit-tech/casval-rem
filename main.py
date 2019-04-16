from flask import Flask

from apis import api

app = Flask(__name__)

app.config["RESTPLUS_MASK_SWAGGER"] = False

api.init_app(app)
