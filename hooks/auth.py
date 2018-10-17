#!/usr/bin/python
# coding:utf-8

import dredd_hooks as hooks
import json


@hooks.before("Auth > 管理者の認証 > 管理者の認証")
def skip_get_auth(transaction):
    print(transaction["request"])
    transaction["request"]["body"] = json.dumps({"password": "admin123"})
