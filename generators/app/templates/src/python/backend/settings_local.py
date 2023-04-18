import os

import structlog

from .settings_base import *  # noqa: F401, F403
from .settings_base import BASE_DIR

# LOGGING


_shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.PositionalArgumentsFormatter(),
]

_builtin_processors = [
    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
    # Use console renderer for local development
    structlog.dev.ConsoleRenderer(colors=True),
]

_builtin_pre_chain = [*_shared_processors]

_structlog_processors = [
    structlog.stdlib.filter_by_level,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.UnicodeDecoder(),
    *_shared_processors,
    # Wrap for builtin logging as very last processor
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": _builtin_processors,
            "foreign_pre_chain": _builtin_pre_chain,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}

structlog.configure(
    processors=_structlog_processors,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "static"))
STATIC_URL = "/static/"
STATICFILES_DIRS = []
