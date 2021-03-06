import concurrent.futures
import time

import requests

REM_SERVER_HOST = "http://127.0.0.1:5000/"

PENDING_TASK_ENDPOINT = "handler/pending/"
RUNNING_TASK_ENDPOINT = "handler/running/"
STOPPED_TASK_ENDPOINT = "handler/stopped/"
FAILED_TASK_ENDPOINT = "handler/failed/"
DELETED_TASK_ENDPOINT = "handler/deleted/"

PENDING_TASK_INTERVAL = 1 * 60  # 1 minute
RUNNING_TASK_INTERVAL = 1 * 60  # 1 minute
STOPPED_TASK_INTERVAL = 1 * 60  # 1 minute
FAILED_TASK_INTERVAL = 1 * 60  # 1 minutes
DELETED_TASK_INTERVAL = 3 * 60  # 3 minutes


def handlePendingTask():
    while True:
        invoke(PENDING_TASK_ENDPOINT)
        time.sleep(PENDING_TASK_INTERVAL)


def handleRunningTask():
    while True:
        invoke(RUNNING_TASK_ENDPOINT)
        time.sleep(RUNNING_TASK_INTERVAL)


def handleStoppedTask():
    while True:
        invoke(STOPPED_TASK_ENDPOINT)
        time.sleep(STOPPED_TASK_INTERVAL)


def handleFailedTask():
    while True:
        invoke(FAILED_TASK_ENDPOINT)
        time.sleep(FAILED_TASK_INTERVAL)


def handleDeletedTask():
    while True:
        invoke(DELETED_TASK_ENDPOINT)
        time.sleep(DELETED_TASK_INTERVAL)


def invoke(endpoint):
    headers = {"X-AppEngine-Cron": "true"}
    url = REM_SERVER_HOST + endpoint
    return requests.get(url, headers=headers)


def main():
    executor = concurrent.futures.ThreadPoolExecutor()
    executor.submit(handlePendingTask)
    executor.submit(handleRunningTask)
    executor.submit(handleStoppedTask)
    executor.submit(handleFailedTask)
    executor.submit(handleDeletedTask)


print(' * Serving local task scheduler "cron.py"')


if __name__ == "__main__":
    main()
