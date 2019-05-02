import concurrent.futures
import os
import time

import requests

PENDING_TASK_INTERVAL = 1 * 60  # 1 minute
RUNNING_TASK_INTERVAL = 1 * 60  # 1 minute
STOPPED_TASK_INTERVAL = 1 * 60  # 1 minute
FAILED_TASK_INTERVAL = 3 * 60  # 3 minutes
DELETED_TASK_INTERVAL = 5 * 60  # 5 minutes

PENDING_TASK_ENDPOINT = "/handler/pending"
RUNNING_TASK_ENDPOINT = "/handler/running"
STOPPED_TASK_ENDPOINT = "/handler/stopped"
FAILED_TASK_ENDPOINT = "/handler/failed"
DELETED_TASK_ENDPOINT = "/handler/deleted"

REQUEST_SCHEMA = "http://"


class LocalTaskScheduler:
    @staticmethod
    def run():
        executor = concurrent.futures.ThreadPoolExecutor()
        executor.submit(LocalTaskScheduler.handlePendingTask)
        executor.submit(LocalTaskScheduler.handleRunningTask)
        executor.submit(LocalTaskScheduler.handleStoppedTask)
        executor.submit(LocalTaskScheduler.handleFailedTask)
        executor.submit(LocalTaskScheduler.handleDeletedTask)
        return

    @staticmethod
    def handlePendingTask():
        while True:
            LocalTaskScheduler.invoke(PENDING_TASK_ENDPOINT)
            time.sleep(PENDING_TASK_INTERVAL)

    @staticmethod
    def handleRunningTask():
        while True:
            LocalTaskScheduler.invoke(RUNNING_TASK_ENDPOINT)
            time.sleep(RUNNING_TASK_INTERVAL)

    @staticmethod
    def handleStoppedTask():
        while True:
            LocalTaskScheduler.invoke(STOPPED_TASK_ENDPOINT)
            time.sleep(STOPPED_TASK_INTERVAL)

    @staticmethod
    def handleFailedTask():
        while True:
            LocalTaskScheduler.invoke(FAILED_TASK_ENDPOINT)
            time.sleep(FAILED_TASK_INTERVAL)

    @staticmethod
    def handleDeletedTask():
        while True:
            LocalTaskScheduler.invoke(DELETED_TASK_ENDPOINT)
            time.sleep(DELETED_TASK_INTERVAL)

    @staticmethod
    def invoke(endpoint):
        return requests.get(REQUEST_SCHEMA + os.getenv("SERVER_NAME", "127.0.0.1:5000") + endpoint)
