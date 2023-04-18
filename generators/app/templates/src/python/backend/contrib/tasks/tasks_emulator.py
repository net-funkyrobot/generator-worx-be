import atexit
import datetime
import os
import pickle
import threading
import time
from typing import Callable, Dict, List, Optional

import jsonpickle
from structlog.stdlib import get_logger

from .schema import TaskOptions

_logger = get_logger(__name__)


def patch_tasks_emulator(persistence=True):
    def _handler(pickled_data: bytes, queue_name: str):
        service_obj = pickle.loads(pickled_data)
        _logger.info("Executing task: {0}".format(service_obj))
        service_obj.run()

    emulator = Emulator(_handler, hibernation=persistence)

    def _schedule_emulator_task(pickled_data: bytes, task_options: TaskOptions):
        _logger.info("Enquing task: {0}".format(task_options.name))
        schedule_time = task_options.eta
        if task_options.countdown:
            schedule_time = datetime.datetime.now() + datetime.timedelta(
                seconds=task_options.countdown
            )

        emulator.create_task(task_options.queue, pickled_data, schedule_time)

    import backend.contrib.tasks

    # Monkey patch _schedule task function
    backend.contrib.tasks.tasks._schedule_task = _schedule_emulator_task


class _Task:
    def __init__(self, payload, queue_name, scheduled_for: float = None):
        self.payload = payload
        self.scheduled_for = scheduled_for or time.time()
        self.queue_name = queue_name


class Emulator:
    """
    The queues in the Emulator are not FIFO. Rather, they are priority queues:
    Elements are popped in the order of the time they are scheduled for, and
    only after the scheduled time.
    """

    __hibernation_file = os.path.abspath("hibernate-emulator-task-queue.json")

    def __init__(self, task_handler: Callable[[bytes, str], None], hibernation=True):
        """
        :param task_handler: A callback function: It will receive the tasks
        :param hibernation: If True, queue state will be persisted at shutdown
            and reloaded at startup. If False, neither will be done.
        """
        assert task_handler, "Need a task handler function"
        self.__lock = threading.Lock()
        self.__task_handler = task_handler
        self.__queues: Dict[str, List[_Task]] = {}
        if hibernation:
            atexit.register(self._hibernate)
            self.__queues = self.__load_from_hibernation()

        tot = self.total_enqueued_tasks()
        if tot:  # Walrus in Python 3.8!
            _logger.info("Loaded %d tasks in %s queues", tot, len(self.__queues))

        self.__queue_threads: dict[str, threading.Thread] = {}

        # Remove hibernation file whether we just loaded or are skipping hubernation.
        self.__remove_hibernation_file()
        for queue_name in self.__queues:  # Launch threads for loaded queues, if any.
            self.__launch_queue_thread(queue_name)

    def __load_from_hibernation(self):
        try:
            with open(self.__hibernation_file, "r") as f:
                json_s = f.read()
                return jsonpickle.decode(json_s)
        except FileNotFoundError:
            return {}

    def __remove_hibernation_file(self):
        try:
            os.remove(self.__hibernation_file)
        except FileNotFoundError:
            pass

    def _hibernate(self):
        if self.total_enqueued_tasks():
            with open(self.__hibernation_file, "w") as f:
                json_s = jsonpickle.encode(self.__queues, indent=2)
                f.write(json_s)
                _logger.info("Persisted queue state to %s", self.__hibernation_file)

    def __process_queue(self, queue_path):
        while True:
            task: Optional[_Task]
            task = None
            with self.__lock:
                queue = self.__queues[queue_path]
                if queue:
                    peek = queue[0]
                    now: float = time.time()
                    if peek.scheduled_for <= now:
                        task = queue.pop(0)  # Pop from the beginning; push to the end
            if task:
                self.__task_handler(task.payload, task.queue_name)

            time.sleep(0.01)

    def create_task(
        self,
        queue_name: str,
        payload,
        scheduled_for: datetime.datetime,
    ):
        """
        Schedules a task.

        Args:
            queue_name: If the queue does not yet exist in this emulator, it
                will be created.
            payload: A string that will be passed to the handler.
            scheduled_for: When this should be delivered. If None or 0, will
                schedule for immediate delivery.
        """
        scheduled_for = scheduled_for or datetime.datetime.now()
        with self.__lock:
            if queue_name not in self.__queues:
                self.__queues[queue_name] = []
                self.__launch_queue_thread(queue_name)
            queue = self.__queues[queue_name]
            task = _Task(payload, queue_name, scheduled_for.timestamp())
            queue.append(task)
            queue.sort(key=lambda t: t.scheduled_for)

    def __launch_queue_thread(self, queue_name):
        new_thread = threading.Thread(
            target=self.__process_queue,
            name=f"Thread-{queue_name}",
            args=[queue_name],
            daemon=True,
        )
        self.__queue_threads[queue_name] = new_thread
        new_thread.start()

    def total_enqueued_tasks(self):
        return sum(len(q) for q in self.__queues.values())
