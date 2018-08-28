from collections import OrderedDict
from dotenv import load_dotenv

import json
import os

path = os.path.abspath(".")
dir_path = os.path.dirname(path)

tmp_json_path = "/template_config.json"
tf_path = "/terraform.tfstate"

local_env_path = ".env.local"
dev_env_path = ".env.dev"

output_json_path = "/config.json"

local_env = os.path.join(os.path.dirname("."), local_env_path)
dev_env = os.path.join(os.path.dirname("."), dev_env_path)
load_dotenv(local_env)
load_dotenv(dev_env)


tf_to_conf_key = [
    ("report_bucket", "S3_BUCKET_NAME"),
    ("sg", "security_group_ids"),
    ("sn_primary", "subnet_ids"),
    ("sn_secondary", "subnet_ids"),
]


def getenv(val):
    value = os.environ.get(val)
    if val[-4:] == "_INT":
        value = int(value)
    print("env: ", val, " : ", value)
    return value


def search_val(arg: dict):
    if isinstance(arg, str):
        if arg[0] == "$":
            arg = getenv(arg[1:])

    elif isinstance(arg, list):
        for x in range(len(arg)):
            arg[x] = search_val(arg[x])

    elif isinstance(arg, dict):
        keys = arg.keys()
        for key in keys:
            arg[key] = search_val(arg[key])

    return arg


def config_subs(tmp_json, tf_json, keys):
    for tf_key, conf_key in keys:
        tf_value = tf_json["modules"][0]["outputs"][tf_key]["value"]
        if conf_key in ["security_group_ids", "subnet_ids"]:
            tmp_json["stages"]["dev"][conf_key].append(tf_value)
        else:
            tmp_json["stages"]["local"]["environment_variables"][conf_key] = tf_value
            tmp_json["stages"]["dev"]["environment_variables"][conf_key] = tf_value

    return tmp_json


def main():
    with open(path + tmp_json_path) as f:
        tmp_json = json.load(f, object_pairs_hook=OrderedDict)
        tmp_json = search_val(tmp_json)

    with open(dir_path + tf_path) as f:
        tf_json = json.load(f)
        make_json = config_subs(tmp_json, tf_json, tf_to_conf_key)

    with open(path + output_json_path, mode="w") as f:
        json.dump(make_json, f, indent=4)


if __name__ == "__main__":
    main()
