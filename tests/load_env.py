import json
import os

path = os.path.abspath(".")
tmp_json_path = "/config.json"
main_json_path = ".chalice" + tmp_json_path


def loadenv(stagename="local"):
    with open(main_json_path) as f:
        config_json = json.load(f)
    apply_config = config_json["stages"][stagename]["environment_variables"]
    for name in apply_config:
        os.environ[name] = apply_config[name]
