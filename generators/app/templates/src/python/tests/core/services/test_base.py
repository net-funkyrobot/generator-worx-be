from backend.contrib.service_base import ServiceResult, catch_service_errors


class __DummyService:
    @catch_service_errors
    def run() -> ServiceResult[None]:
        raise Exception("A dummy error that happens inside the service logic")


def test_catch_service_errors_decorator():
    # SUT
    result = __DummyService().run()

    assert not result.success
    assert len(result.errors) > 0
    assert isinstance(result.errors[0], Exception)
