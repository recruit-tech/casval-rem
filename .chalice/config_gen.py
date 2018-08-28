import json
from collections import OrderedDict
import pprint
import os
path = os.path.abspath(".")
dir_path = os.path.dirname(path)

tmp_json_path = '/template_config.json'
tf_path = '/terraform.tfstate'
env_path = '/env.local'
env_path = '/env.dev'
output_json_path = '/config.json'

tf_to_conf_key = [
    ("report_bucket", "S3_BUCKET_NAME"),
    ("sg", "security_group_ids"),
    ("sn_primary", "subnet_ids"),
    ("sn_secondary", "subnet_ids")
]


def config_subs(tmp_json, tf_json, keys):
    for tf_key, conf_key in keys:
        tf_value = tf_json["modules"][0]["outputs"][tf_key]["value"]
        print(tf_value)
        if conf_key in ["security_group_ids", "subnet_ids"]:
            tmp_json["stages"]["dev"][conf_key].append(tf_value)
        else:
            tmp_json["stages"]["local"]["environment_variables"][conf_key] = tf_value
            tmp_json["stages"]["dev"]["environment_variables"][conf_key] = tf_value

    return tmp_json


def main():
    try:
        with open(path + tmp_json_path) as f:
            tmp_json = json.load(f, object_pairs_hook=OrderedDict)
            print(tmp_json)

        with open(dir_path + tf_path) as f:
            tf_json = json.load(f)
            make_json = config_subs(tmp_json, tf_json, tf_to_conf_key)
            print(tf_json)

        with open(path + output_json_path, mode='w') as f:
            print(make_json)
            json.dump(make_json, f, indent=4)

    except OSError as e:
        print(e)
    except KeyError as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
