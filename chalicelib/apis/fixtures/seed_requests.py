from argparse import ArgumentParser
from collections import OrderedDict

import glob
import json
import requests

local_url = "http://127.0.0.1:3000"
endpoint = "/tests/setup/db"

fixturelist = glob.glob("./chalicelib/apis/fixtures/*.json")


def requests_run(flag_str, args=None):

    if flag_str == "drop":
        payload = {
            "models": [
                "chalicelib.core.models.Audit",
                "chalicelib.core.models.Scan",
                "chalicelib.core.models.Result",
                "chalicelib.core.models.Vuln",
                "chalicelib.core.models.Contact",
            ]
        }
        if not (args is None):
            for i in args:
                payload["models"].append(i)
        r = requests.delete(
            local_url + endpoint, data=json.dumps(payload), headers={"Content-Type": "application/json"}
        )
        print(r.json())
    elif flag_str == "seed":
        jsonlist = []
        for path in fixturelist:
            with open(path) as f:
                j = json.load(f, object_pairs_hook=OrderedDict)
                for ej in j:
                    jsonlist.append(ej)

        r = requests.post(
            local_url + endpoint, json.dumps(jsonlist), headers={"Content-Type": "application/json"}
        )
        print(r)


def command_drop(args):
    requests_run("drop")


def command_seed(args):
    requests_run("seed")


def get_args():
    parser = ArgumentParser(prog="seeds_entry")
    subparsers = parser.add_subparsers()

    parent_drop = subparsers.add_parser("drop", help="db table drop")
    parent_drop.set_defaults(handler=command_drop)

    parent_seed = subparsers.add_parser("seed", help="db table init data input")
    parent_seed.set_defaults(handler=command_seed)

    args = parser.parse_args()

    return args, parser


def main():
    args, parser = get_args()
    print(args)
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
