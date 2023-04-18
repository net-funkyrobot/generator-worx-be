from datetime import datetime
from typing import Optional

from pydantic import BaseModel, conint, validator

from .environment import gae_version


class RoutingOptions(BaseModel):
    version: str = gae_version()
    serivce: Optional[str]
    instance: Optional[str]


_DEFAULT_QUEUE = "default"
_DEFAULT_HANDLER_NAME = "tasks_deferred_handler"


class TaskOptions(BaseModel):
    name: Optional[str]
    created_at: Optional[datetime]
    small_task: bool = False
    using: str = "default"
    transactional: bool = False  # TODO: Should this be False by default?
    countdown: Optional[conint(gt=0)]
    eta: Optional[datetime]
    routing: Optional[RoutingOptions]
    handler_url: str = _DEFAULT_HANDLER_NAME
    extra_task_headers: dict = {}
    queue: str = _DEFAULT_QUEUE

    @validator("using")
    def using_has_valid_connection_name(cls, v):
        from django.db import connections

        if v not in connections:
            raise ValueError(
                "'using' not a valid DB connection in {0}".format(
                    ",".join(connections.keys()),
                )
            )

        return v
