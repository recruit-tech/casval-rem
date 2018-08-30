from collections import OrderedDict

import json
import os
import re

path = os.path.abspath("..")
repatter = re.compile("^__.*__.*")


tmp_json_path = "/config.json"
tf_path = "/terraform.tfstate"
output_json_path = "/.chalice" + tmp_json_path


class PyColor:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    END = "\033[0m"
    BOLD = "\038[1m"
    UNDERLINE = "\033[4m"
    INVISIBLE = "\033[08m"
    REVERCE = "\033[07m"


def get_tf(val, tf_json):
    tf_value = tf_json["modules"][0]["outputs"][val]["value"]
    print(PyColor.GREEN + "tf: ", val, " : ", tf_value + PyColor.END)
    return tf_value


def is_tf_stage(stage_name, tf_json):
    if stage_name == tf_json["modules"][0]["outputs"]["stage"]["value"]:
        return True

    return False


def search_val(json_ctx, tf_json: dict):

    if isinstance(json_ctx, str):
        match = repatter.match(json_ctx)

        if match:
            match_string = match.group()
            stage_name = match_string.split("__")[1]

            if is_tf_stage(stage_name, tf_json):
                json_ctx = get_tf(json_ctx[len(stage_name) + 4:], tf_json)
            else:
                print(PyColor.RED + "tf: ", json_ctx, " : ", "not patter match" + PyColor.END)

    elif isinstance(json_ctx, list):
        for x in range(len(json_ctx)):
            json_ctx[x] = search_val(json_ctx[x], tf_json)

    elif isinstance(json_ctx, dict):
        keys = json_ctx.keys()
        for key in keys:
            json_ctx[key] = search_val(json_ctx[key], tf_json)

    return json_ctx


def main():
    with open(path + tmp_json_path) as f:
        tmp_json = json.load(f, object_pairs_hook=OrderedDict)

    with open(path + tf_path) as f:
        tf_json = json.load(f)
        tmp_json = search_val(tmp_json, tf_json)

    with open(path + output_json_path, mode="w") as f:
        json.dump(tmp_json, f, indent=4)


if __name__ == "__main__":
    main()
