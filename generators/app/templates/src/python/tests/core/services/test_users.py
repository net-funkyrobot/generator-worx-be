from zoneinfo import ZoneInfo

import pytest
from backend.core.models import EndUser
from backend.core.services.userbase import SyncNewUsers
from django.utils.timezone import datetime
from firebase_admin import firestore
from tests.utils import patch_firestore


@pytest.mark.django_db
@patch_firestore
def test_first_sync(fs_user_profile_factory):
    """Test synchronising users works."""
    fs_client = firestore.client()

    fs_users = [fs_user_profile_factory() for _ in range(4)]

    for user in fs_users:
        fs_client.collection("users").add(user.dict())

    assert EndUser.objects.count() == 0

    # SUT
    result = SyncNewUsers().run()

    assert result.success

    assert EndUser.objects.count() == len(fs_users)


@pytest.mark.django_db
@patch_firestore
def test_sync_from(user_profile_factory, fs_user_profile_factory):
    """Test synchronising users works."""
    fs_client = firestore.client()

    # Create an existing user (added to Firestore) and 4 new ones
    existing_fs_user = fs_user_profile_factory(
        created=datetime(2022, 6, 4, tzinfo=ZoneInfo("UTC")),
    )
    _, doc = fs_client.collection("users").add(existing_fs_user.dict())
    user_profile_factory(
        firebase_auth_user_id=doc.id,
        email=existing_fs_user.email,
        created_at=existing_fs_user.created,
    )
    new_fs_users = [
        fs_user_profile_factory(
            created=datetime(2022, 7, 18, tzinfo=ZoneInfo("UTC")),
        )
        for _ in range(4)
    ]
    fs_users = [existing_fs_user, *new_fs_users]

    # Add the 4 new users to Firestore
    for user in new_fs_users:
        fs_client.collection("users").add(user.dict())

    assert EndUser.objects.count() == 1

    # SUT
    SyncNewUsers().run()

    # We should have 5 users and not 6 (because one already exists)
    assert EndUser.objects.count() == len(fs_users)
