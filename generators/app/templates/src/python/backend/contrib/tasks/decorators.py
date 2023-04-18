from functools import wraps

from django.http import HttpResponseForbidden

from .environment import is_in_cron, is_in_task


def task_only(view_function):
    """Restrict access to tasks (and crons) to the application itself only.

    Used as a decorator.
    """

    @wraps(view_function)
    def replacement(request, *args, **kwargs):
        if not any((is_in_task(), is_in_cron())):
            return HttpResponseForbidden("Access denied.")

        return view_function(request, *args, **kwargs)

    return replacement


def task_or_superuser_only(view_function):
    """Restrict access to tasks (and crons) to the application itself only and
    superusers.

    Used as a decorator."""

    @wraps(view_function)
    def replacement(request, *args, **kwargs):
        is_superuser = (
            getattr(request, "user", None)
            and request.user.is_authenticated
            and request.user.is_superuser
        )

        if not any((is_superuser, is_in_task(), is_in_cron())):
            return HttpResponseForbidden("Access denied.")

        return view_function(request, *args, **kwargs)

    return replacement
