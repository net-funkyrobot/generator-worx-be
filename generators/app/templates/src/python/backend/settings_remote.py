import structlog
from django.dispatch import receiver
from django_structlog.signals import bind_extra_request_metadata

from .settings_base import *  # noqa: F401, F403
from .settings_base import GOOGLE_CLOUD_PROJECT

# LOGGING


def _transform_for_gcloud_logging(logger, log_method, event_dict):
    # Rename 'event' to 'message'
    event_dict["message"] = event_dict.get("event")
    del event_dict["event"]

    # Rename 'level' to 'severity'
    event_dict["severity"] = event_dict.get("level")
    del event_dict["level"]

    # Map severity levels to GCloud versions and make uppercase
    if event_dict["severity"].lower() == "notset":
        event_dict["severity"] = "debug"
    event_dict["severity"] = event_dict["severity"].upper()

    return event_dict


_shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.PositionalArgumentsFormatter(),
    # Transform keys and values to work with Google Cloud Logging
    _transform_for_gcloud_logging,
]

_builtin_processors = [
    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
    # Use JSON formatting on remote as opposed to console rendering
    structlog.processors.JSONRenderer(),
]

_builtin_pre_chain = [*_shared_processors]

_structlog_processors = [
    structlog.stdlib.filter_by_level,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.UnicodeDecoder(),
    *_shared_processors,
    # Transform keys and values to work with Google Cloud Logging
    structlog.processors.format_exc_info,
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
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


@receiver(bind_extra_request_metadata)
def bind_appengine_trace_context_id(request, logger, **kwargs):
    trace_header = request.headers.get("X-Cloud-Trace-Context", None)

    project_id = GOOGLE_CLOUD_PROJECT

    if project_id and trace_header:
        logger.bind(
            **{
                "logging.googleapis.com/trace": "projects/{0}/traces/{1}".format(
                    project_id,
                    trace_header.split("/")[0],
                ),
            },
        )
