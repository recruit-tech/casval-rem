#!/usr/bin/python
# coding:utf-8

import dredd_hooks as hooks


@hooks.before("Vulnerabilities > 脆弱性一覧の取得 > 脆弱性一覧の取得")
def skip_vuln_list_get(transaction):
    transaction["skip"] = True


@hooks.before("Vulnerabilities > 脆弱性情報 > 取得")
def skip_vuln_get(transaction):
    transaction["skip"] = True


@hooks.before("Vulnerabilities > 脆弱性情報 > 修正要否の変更")
def skip_vuln_patch(transaction):
    transaction["skip"] = True
