#!/usr/bin/python
# coding:utf-8


import dredd_hooks as hooks


# use id :3cd708cefd58401f9d43ff953f063469
@hooks.before("Scan > 新規スキャンの登録 > 新規スキャンの登録")
def skip_post_scan(transaction):
    transaction["skip"] = True
    # transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063469/scan"
    # transaction["request"]["body"] = json.dumps({"target": "160.17.99.174"})


@hooks.before("Scan > スキャン情報 > 取得")
def skip_get_scan(transaction):
    transaction["skip"] = True
    # transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063469/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc"


@hooks.before("Scan > スキャン情報 > 更新")
def skip_update_scan(transaction):
    transaction["skip"] = True
    # transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063469/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc"


@hooks.before("Scan > スキャン情報 > 削除")
def skip_delete_scan(transaction):
    transaction["skip"] = True
    # transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063469/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc"


# use id :3cd708cefd58401f9d43ff953f063470
@hooks.before("Scan > スキャンスケジュール > 更新")
def skip_schedule_update_scan(transaction):
    transaction["skip"] = True
    # transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063470/scan/21d6cd7b33e84fbf9a2898f4ea7f90cd/schedule"


@hooks.before("Scan > スキャンスケジュール > 削除")
def skip_schedule_delete_scan(transaction):
    transaction["skip"] = True
    # transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063470/scan/21d6cd7b33e84fbf9a2898f4ea7f90cd/schedule"

