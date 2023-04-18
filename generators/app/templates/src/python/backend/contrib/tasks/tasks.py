import functools
import pickle
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional
from urllib.parse import unquote

import structlog
from django.db import connections
from django.urls import reverse
from django.utils import timezone
from google.api_core import exceptions
from google.cloud import tasks_v2
from google.protobuf.timestamp_pb2 import Timestamp

from .environment import google_cloud_project, tasks_location
from .schema import TaskOptions

_logger = structlog.get_logger(__name__)


_TASKQUEUE_HEADERS = {"Content-Type": "application/octet-stream"}
_CLOUD_TASKS_PROJECT = google_cloud_project()
_CLOUD_TASKS_LOCATION = tasks_location()


class TaskError(Exception):
    """Base class for exceptions in this module."""


class PermanentTaskError(TaskError):
    """Indicates that a task failed, and will never succeed."""


def _run_from_database(deferred_task_id):
    """Retrieve a task from the database and execute it."""

    def run(data):
        # Unpickle and execute task.
        try:
            service_instance = pickle.loads(data)
        except Exception as e:
            raise PermanentTaskError(e)
        else:
            return service_instance.run()

    # Inline import to support importing this module before Django is initialized
    from .models import LargeDeferredTask

    entity = LargeDeferredTask.objects.filter(pk=deferred_task_id).first()
    if not entity:
        raise PermanentTaskError()

    try:
        run(entity.data)
        entity.delete()
    except PermanentTaskError:
        entity.delete()
        raise


def _serialize(obj: object):
    return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)


def _get_task_name(obj: Any, task_created_at: datetime) -> str:
    klass = obj.__class__
    task_id = str(uuid.uuid4())[:8]
    if klass.__module__:
        name = "{0}.{1}:{2}-{3}".format(
            klass.__module__,
            klass.__qualname__,
            task_created_at,
            task_id,
        )
    else:
        name = "{0}:{1}-{2}".format(klass.__qualname__, task_created_at, task_id)

    return name


def _schedule_task(pickled_data: bytes, task_options: TaskOptions):
    client = tasks_v2.CloudTasksClient()
    deferred_task = None

    path = client.queue_path(
        _CLOUD_TASKS_PROJECT,
        _CLOUD_TASKS_LOCATION,
        task_options.queue,
    )

    task_headers = dict(_TASKQUEUE_HEADERS)
    task_headers.update(task_options.extra_task_headers)

    schedule_time = task_options.eta
    if task_options.countdown:
        schedule_time = timezone.now() + timedelta(seconds=task_options.countdown)

    if schedule_time:
        # If a schedule time has bee requested, we need to convert
        # to a Timestamp
        ts = Timestamp()
        ts.FromDatetime(schedule_time)
        schedule_time = ts

    created_at_ts = Timestamp()
    created_at_ts.FromDatetime(task_options.created_at)

    task = {
        "name": "{0}/tasks/{1}".format(path, task_options.name),
        "create_time": created_at_ts,
        "schedule_time": schedule_time,
        "app_engine_http_request": {  # Specify the type of request.
            "http_method": "POST",
            "relative_uri": unquote(reverse(task_options.handler_url)),
            "body": pickled_data,
            "headers": task_headers,
            "app_engine_routing": task_options.routing.dict()
            if task_options.routing
            else None,
        },
    }

    try:
        # Defer the task
        task = client.create_task(parent=path, task=task)  # FIXME: Handle transactional

        # Delete the key as it wasn't needed
        if deferred_task:
            deferred_task.delete()
    except exceptions.InvalidArgument as e:
        if "Task size too large" not in str(e):
            raise

        # Create a db entity unless this has been explicitly marked as a small task
        if task_options.small_task:
            raise

        # Inline import to support importing this module before Django is initialized
        from .models import LargeDeferredTask

        deferred_task = LargeDeferredTask.objects.create(data=pickled_data)

        # Replace the task body with one containing a function to run the
        # original task body which is stored in the datastore entity.
        task["body"] = _serialize(_run_from_database, deferred_task.pk)

        client.create_task(path, task)  # FIXME: Handle transactional
    except:  # noqa
        # Any other exception? Delete the key
        if deferred_task:
            deferred_task.delete()
        raise


def defer(obj: object, task_options: Optional[TaskOptions] = None):
    """
    This is a reimplementation of the defer() function that historically shipped
    with App Engine Standard before the Python 3 runtime.

    It fixes a number of bugs in that implementation, but has some subtle
    differences. In particular, the _transactional flag is not entirely atomic
    - deferred tasks will run on successful commit, but they're not *guaranteed*
    to run if there is an error submitting them.

    If the task is too large to be serialized and passed in the request it uses
    a Django model instance to tempoarilly store the payload. The small task
    limit is 100K.
    """
    assert callable(getattr(obj, "run")), "Task 'obj' must have a run() method."

    task_options = task_options.copy() if task_options else TaskOptions()

    # Populate task name unless custom name given
    created_at = datetime.now()
    task_options.created_at = task_options.created_at or created_at
    task_options.name = task_options.name or _get_task_name(
        obj,
        task_options.created_at,
    )

    # Determine if we run the task at the end of the current transaction
    connection = connections[task_options.using]
    task_options.transactional = (
        task_options.transactional
        if task_options.transactional is not None
        else connection.in_atomic_block
    )

    pickled = _serialize(obj)

    if task_options.transactional:
        # Django connections have an on_commit message that run things on
        # post-commit.
        connection.on_commit(functools.partial(_schedule_task, pickled, task_options))
    else:
        _schedule_task(pickled, task_options)
