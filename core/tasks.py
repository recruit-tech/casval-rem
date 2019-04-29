from abc import ABCMeta
from abc import abstractmethod

from .models import TaskProgressValue
from .models import TaskTable

SCAN_MAX_NUMBER_OF_MESSAGES_IN_QUEUE = 10
SCAN_MAX_PARALLEL_SESSION = 2

HARD_DELETE = False


class TaskAbstract:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def handle():
        pass

    @abstractmethod
    def add(entry):
        pass

    @abstractmethod
    def delete(task_id):
        if HARD_DELETE == True:
            TaskTable.delete().where(TaskTable.id == task_id).execute()
        else:
            TaskTable.update({"progress": TaskProgressValue.DELETED.name}).where(
                TaskTable.id == task_id
            ).execute()
        return True


class PendingTask(TaskAbstract):
    @staticmethod
    def handle():
        print("handle!")
        return {}

    @staticmethod
    def add(entry):
        task = TaskTable(**entry)
        task.save()

        return task

    @staticmethod
    def delete(task_id):
        super().delete(*args, **kwargs)
