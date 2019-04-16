from flask import Flask

from apis import api

app = Flask(__name__)

app.config["RESTPLUS_MASK_SWAGGER"] = False
app.config["SWAGGER_UI_REQUEST_DURATION"] = True
app.config["SWAGGER_UI_DOC_EXPANSION"] = "list"
app.config["SWAGGER_UI_JSONEDITOR"] = True

api.init_app(app)
