from logging import getLogger

from backend.contrib.tasks import defer
from ninja import NinjaAPI
from structlog.stdlib import get_logger

from .services.dummy import DummyBackgroundTask

api = NinjaAPI()

_logger = get_logger(__name__)
_core_logger = getLogger(__name__)


@api.post("/dummy-resource")
def resource_with_background_task(request):
    _logger.error("Hello world!")
    _core_logger.error("Hello Python")
    defer(DummyBackgroundTask(some_param=1))
