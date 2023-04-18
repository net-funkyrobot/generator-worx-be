import os
import threading
from typing import Optional

_TASK_ENV = threading.local()


def google_cloud_project() -> Optional[str]:
    return os.environ.get("GOOGLE_CLOUD_PROJECT")


def application_id(default="e~example") -> str:
    # Fallback to example on local or if this is not specified in the
    # environment already
    result = os.environ.get("GAE_APPLICATION", default)
    return result


def gae_version() -> Optional[str]:
    """Return the current GAE version."""
    return os.environ.get("GAE_VERSION")


def is_in_task() -> bool:
    """Return True if the request is a task, False otherwise."""
    return bool(getattr(_TASK_ENV, "task_name", False))


def is_in_cron() -> bool:
    """Return True if the request is in a cron, False otherwise."""
    return bool(getattr(_TASK_ENV, "is_cron", False))


def task_name() -> Optional[str]:
    """Return the name of the current task if any, else None."""
    return getattr(_TASK_ENV, "task_name", None)


def task_retry_count() -> Optional[int]:
    """Return the task retry count or None if this isn't a task."""
    try:
        return int(getattr(_TASK_ENV, "task_retry_count", None))
    except (TypeError, ValueError):
        return None


def task_queue_name() -> Optional[str]:
    """Return the name of the current task queue else 'default'."""
    if is_in_task():
        return getattr(_TASK_ENV, "queue_name", "default")
    return None


def task_execution_count() -> Optional[int]:
    if is_in_task():
        return getattr(_TASK_ENV, "task_execution_count", 0)
    return None


def tasks_location() -> Optional[str]:
    """Get the Cloud Tasks location based on the application ID prefix."""
    lookup = {
        "b": "asia-northeast1",
        "d": "us-east4",
        "e": "europe-west1",
        "f": "australia-southeast",
        "g": "europe-west2",
        "h": "europe-west3",
        "i": "southamerica-east1",
        "j": "asia-south1",
        "k": "northamerica-northeast1",
        "m": "us-west2",
        "n": "asia-east2",
        "o": "europe-west6",
        "p": "us-east1",
        "s": "us-central1",
        "u": "asia-northeast2",
        "v": "asia-northeast3",
        "zas": "asia-southeast1",
        "zde": "asia-east1",
        "zet": "asia-southeast2",
        "zlm": "europe-central2",
        "zuw": "us-west1",
        "zwm": "us-west3",
        "zwn": "us-west4",
    }

    app_id_with_prefix = application_id()
    location_id = app_id_with_prefix.split("~", 1)[0]
    return lookup.get(location_id)
