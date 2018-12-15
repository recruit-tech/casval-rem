#!/usr/bin/python
# coding:utf-8


from datetime import datetime

import dredd_hooks as hooks

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
now = datetime.now()


# use id :3cd708cefd58401f9d43ff953f063469
# # not report_url
@hooks.before("Scan > 新規スキャンの登録 > 新規スキャンの登録")
def skip_post_scan(transaction):
    transaction["skip"] = True
    # transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063469/scan"
    # transaction["request"]["body"] = json.dumps({"target": "160.17.99.174"})


# not report_url
@hooks.before("Scan > スキャン情報 > 取得")
def skip_get_scan(transaction):
    transaction["skip"] = True
    # transaction["fullPath"]
    #  = "/audit/3cd708cefd58401f9d43ff953f063469/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc"


# not report_url
@hooks.before("Scan > スキャン情報 > 更新")
def skip_update_scan(transaction):
    transaction["skip"] = True
    # transaction["fullPath"]
    # = "/audit/3cd708cefd58401f9d43ff953f063469/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc"


@hooks.before("Scan > スキャン情報 > 削除")
def skip_delete_scan(transaction):
    transaction["fullPath"] = "/audit/3cd708cefd58401f9d43ff953f063469/scan/21d6cd7b33e84fbf9a2898f4ea7f90cc"


# use id :3cd708cefd58401f9d43ff953f063470
@hooks.before("Scan > スキャンスケジュール > 更新")
def skip_schedule_update_scan(transaction):
    transaction["skip"] = True
    # transaction[
    #     "fullPath"
    # ] = "/audit/3cd708cefd58401f9d43ff953f063470/scan/21d6cd7b33e84fbf9a2898f4ea7f90cd/schedule"
    # nexttime_s = now + timedelta(hours=1)
    # nexttime_e = now + timedelta(hours=7)
    # transaction["request"]["body"] = json.dumps(
    #     {
    #         "schedule": {
    #             "start_at": nexttime_s.strftime(DATETIME_FORMAT),
    #             "end_at": nexttime_e.strftime(DATETIME_FORMAT),
    #         }
    #     }
    # )


@hooks.before("Scan > スキャンスケジュール > 削除")
def skip_schedule_delete_scan(transaction):
    transaction["skip"] = True
    # transaction[
    #     "fullPath"
    # ] = "/audit/3cd708cefd58401f9d43ff953f063470/scan/21d6cd7b33e84fbf9a2898f4ea7f90cd/schedule"
