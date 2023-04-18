from datetime import datetime
from typing import Optional

from backend.contrib.service_base import ServiceResult, catch_service_errors
from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from firebase_admin import firestore
from mailerlite import MailerLiteApi
from ninja import Schema

from ..models import EndUser
from ..schemas import FsUserProfile

_MAILERLITE_API_PAGE_SIZE = 50


class SyncMailingList:
    @catch_service_errors
    def run(self) -> ServiceResult[None]:
        client = MailerLiteApi(settings.MAILERLITE_API_TOKEN)
        group = settings.MAILERLITE_GROUP

        # Check group exists, get ID, create it if necessary
        all_groups = client.groups.all()
        group_matches = [g for g in all_groups if g.name == group]

        if group_matches:
            group_id = group_matches[0].id
        else:
            new_group = client.groups.create(name=group)
            group_id = new_group.id

        # Query for new users, paginate, bulk subscribe users using client
        new_user_emails = EndUser.objects.filter(
            opt_in_communications=True,
            subscribed=False,
            has_unsubscribed=False,
        ).values_list("email", flat=True)

        pages = Paginator(new_user_emails, _MAILERLITE_API_PAGE_SIZE)

        for page_num in range(1, pages.num_pages + 1):
            page = pages.page(page_num)

            new_subscribers = client.groups.add_subscribers(
                group_id=group_id,
                subscribers_data=[{"email": email, "name": email} for email in page],
                autoresponders=False,
                resubscribe=True,
            )

            # Update flag and Mailerlite ID on models for successful subscribe
            for sub in new_subscribers:
                EndUser.objects.update(
                    email=sub.email,
                    susbcribed=True,
                    mailing_list_id=sub.id,
                )

        return ServiceResult(success=True)


class SyncNewUsers(Schema):
    """Sync user profile documents from Firestore.

    This creates user profiles in the backend database.
    """

    sync_all: bool = False
    sync_from: Optional[datetime]

    @catch_service_errors
    def run(self) -> ServiceResult[None]:
        last_sync_timestamp = self.sync_from or (
            EndUser.objects.values_list("created_at", flat=True)
            .order_by("-created_at")
            .first()
        )

        store = firestore.client()

        if self.sync_all or last_sync_timestamp is None:
            fb_users = store.collection("users").get()
        else:
            fb_users = (
                store.collection("users")
                .where("created", ">=", last_sync_timestamp)
                .stream()
            )

        # Successfully sync all users or none at all
        # This is so we can retry whole syncs after fixing an error and no
        # user profiles fall down the cracks
        with transaction.atomic():
            for user in fb_users:
                user_profile = FsUserProfile(**user.to_dict())

                EndUser.objects.get_or_create(
                    uid=user.reference.id,
                    email=user_profile.email,
                    opt_in_communications=user_profile.opt_in_communications,
                )

        return ServiceResult(success=True)
