#!/usr/bin/python
# coding:utf-8

import dredd_hooks as hooks

# use id :3cd708cefd58401f9d43ff953f063467


@hooks.before("Audit > 検査一覧の取得 > 検査一覧の取得")
def skip_get_audit(transaction):
    pass


@hooks.before("Audit > 新規検査の登録 > 新規検査の登録")
def skip_post_audit(transaction):
    transaction["fullPath"] = "/audit"


@hooks.before("Audit > 閲覧用トークンの生成 > 閲覧用トークンの生成")
def skip_browsing_token_audit(transaction):
    transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063467/tokens"


@hooks.before("Audit > 検査情報 > 取得")
def skip_get_info_audit(transaction):
    transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063467"


@hooks.before("Audit > 検査情報 > 更新")
def skip_patch_update_audit(transaction):
    transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063467"


@hooks.before("Audit > 検査情報 > 失効")
def skip_delete_info_audit(transaction):
    transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063467"


# use id :3cd708cefd58401f9d43ff953f063468
@hooks.before("Audit > 検査の提出 > 提出")
def skip_post_info_audit(transaction):
    transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063468/submit"


@hooks.before("Audit > 検査の提出 > 取り下げ／却下 > Example 1")
def skip_delete_ex1_audit(transaction):
    transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063468/submit"


@hooks.before("Audit > 検査の提出 > 取り下げ／却下 > Example 2")
def skip_delete_ex2_audit(transaction):
    transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063468/submit"
