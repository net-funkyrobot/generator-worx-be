import logging
import os

from django.conf import settings
from django.http import JsonResponse
from structlog.stdlib import get_logger

_logger = get_logger(__name__)
_core_logger = logging.getLogger(__name__)

_SETTINGS_BLACKLIST = (
    "SECRET_KEY",
    "LANGUAGES",
    "LANGUAGES_BIDI",
)


def debug_raise_exception(request):
    x = 25
    raise Exception("A dummy error: {0}".format(x))


def debug(request):
    _logger.debug("test_debug_log", someparam="Hello")
    _logger.info("test_info_log", someparam="Hello")
    _logger.warning("test_warning_log", someparam="Hello")
    _logger.error("test_error_log", someparam="Hello")
    _logger.critical("test_critical_log", someparam="Hello")

    _core_logger.debug("test_builtin_debug_log")
    _core_logger.info("test_builtin_info_log")
    _core_logger.warning("test_builtin_warning_log")
    _core_logger.error("test_builtin_error_log")
    _core_logger.critical("test_builtin_critical_log")

    debug_info = {
        "settings": {
            k: v for k, v in settings.__dict__.items() if k not in _SETTINGS_BLACKLIST
        },
        "environ": {k: v for k, v in os.environ.items()},
    }

    return JsonResponse(
        data=debug_info,
        json_dumps_params={"indent": 2, "sort_keys": True, "default": str},
    )
