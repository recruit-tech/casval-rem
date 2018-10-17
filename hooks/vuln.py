#!/usr/bin/python
# coding:utf-8

import dredd_hooks as hooks


@hooks.before("Vulnerabilities > 脆弱性一覧の取得 > 脆弱性一覧の取得")
def skip_list_get_vuln(transaction):
    transaction["skip"] = True


@hooks.before("Vulnerabilities > 脆弱性情報 > 取得")
def skip_info_get_vuln(transaction):
    transaction["skip"] = True


@hooks.before("Vulnerabilities > 脆弱性情報 > 修正要否の変更")
def skip_req_fix_patch_vuln(transaction):
    transaction["skip"] = True
