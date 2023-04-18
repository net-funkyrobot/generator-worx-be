import functools
from unittest.mock import patch

from mockfirestore import MockFirestore


def patch_firestore(func):
    """
    Patch the Firestore client.

    Uses a mock client provided by the mock-firestore package.

    Args:
        func (_type_): _description_

    Returns:
        _type_: _description_
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        mock_firestore_client = MockFirestore()
        with patch("firebase_admin.firestore.client") as mock:
            mock.return_value = mock_firestore_client

            return func(*args, **kwargs)

    return wrapper
