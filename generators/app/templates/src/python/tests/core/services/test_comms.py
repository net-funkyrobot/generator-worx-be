import pytest
from backend.core.models import EndUser
from backend.core.services.userbase import SyncMailingList
from django.conf import settings


@pytest.mark.vcr
@pytest.mark.django_db
def test_sync_mailing_list(user_profile_factory):
    assert settings.MAILERLITE_GROUP == "testing"

    for i in range(5):
        user_profile_factory(subscribed_to_mailing_list=True, mailing_list_id=i)

    for _ in range(5):
        user_profile_factory(subscribed_to_mailing_list=False)

    assert EndUser.objects.count() == 10
    assert EndUser.objects.filter(subscribed=True).count() == 5

    result = SyncMailingList().run()

    assert result.success

    # Now all users should be subscribed
    assert EndUser.objects.filter(subscribed=True).count() == 10

    # All users should have a mailing list ID
    all_users = EndUser.objects.all()
    assert all(
        [
            user.mailing_list_id is not None and user.mailing_list_id != ""
            for user in all_users
        ]
    )
