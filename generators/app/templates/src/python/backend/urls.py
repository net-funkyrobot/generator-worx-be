from backend.contrib.debug.views import debug, debug_raise_exception
from backend.core.api import api
from backend.core.cron_tasks import dummy_defer_task, dummy_task
from django.urls import include, path

urlpatterns_cron_tasks = [
    path("dummy-task/", dummy_task, name="dummy-task"),
    path("dummy-defer-task/", dummy_defer_task, name="dummy-defer-task"),
    path("sync-pokemon/", dummy_defer_task, name="sync-pokemon"),
]

urlpatterns = [
    path("api/v1/", api.urls),  # type: ignore
    path(
        "cron-tasks/",
        include((urlpatterns_cron_tasks, "core"), namespace="tasks"),
    ),
    path("debug/", debug, name="debug"),
    path("debug/raise-exception/", debug_raise_exception, name="debug-raise-exception"),
]
