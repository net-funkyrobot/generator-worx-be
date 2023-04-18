from logging import getLogger

from ninja import Schema
from structlog.stdlib import get_logger

_logger = get_logger(__name__)
_core_logger = getLogger(__name__)


class DummyBackgroundTask(Schema):
    some_param: int

    def run(self):
        _logger.error("Hello world! (from background task) {0}".format(self.some_param))
        _core_logger.error("Hello Python (from background task)")
