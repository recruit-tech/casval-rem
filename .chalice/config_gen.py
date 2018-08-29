from collections import OrderedDict
import re

import json
import os

path = os.path.abspath("..")
repatter = re.compile("^__.*__.*")


tmp_json_path = "/config.json"
tf_path = "/terraform.tfstate"
output_json_path = "/.chalice" + tmp_json_path


class PyColor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    END = '\033[0m'
    BOLD = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE = '\033[07m'


def get_tf(val, tf_json):
    tf_value = tf_json["modules"][0]["outputs"][val]["value"]
    print(PyColor.GREEN + "tf: ", val, " : ", tf_value + PyColor.END)
    return tf_value


def search_val(arg: dict, tfarg: dict):
    if isinstance(arg, str):
        if arg[:7] == "__dev__":
            arg = get_tf(arg[7:], tfarg)
        elif arg[:8] == "__prep__":
            arg = get_tf(arg[8:], tfarg)
        elif repatter.match(arg):
            print(PyColor.RED + "tf: ", arg, " : ", "not patter match" + PyColor.END)

    elif isinstance(arg, list):
        for x in range(len(arg)):
            arg[x] = search_val(arg[x], tfarg)

    elif isinstance(arg, dict):
        keys = arg.keys()
        for key in keys:
            arg[key] = search_val(arg[key], tfarg)

    return arg


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

