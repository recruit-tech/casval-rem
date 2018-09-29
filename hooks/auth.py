#!/usr/bin/python
# coding:utf-8

import dredd_hooks as hooks


@hooks.before("Auth > 管理者の認証 > 管理者の認証")
def skip_vuln_list_get(transaction):
    transaction["skip"] = True
