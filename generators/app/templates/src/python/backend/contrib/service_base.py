from functools import wraps
from typing import Generic, Optional, TypeVar

from ninja import Schema  # TODO change this to use pydantic

ReturnType = TypeVar("ReturnType")


class ServiceResult(Schema, Generic[ReturnType]):
    success: bool
    return_value: Optional[ReturnType]
    errors: Optional[list[Exception]]

    class Config:
        arbitrary_types_allowed = True


def catch_service_errors(func):
    """Catch errors return them inside a ServiceResult instance.

    Returns errors as ServiceResult(success=False, errors=[e]).
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # TODO: log out error here
            return ServiceResult(success=False, errors=[e])

    return wrapper
