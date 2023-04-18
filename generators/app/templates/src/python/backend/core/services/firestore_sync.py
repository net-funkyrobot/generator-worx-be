from typing import Callable, Generic, TypeVar

from backend.contrib.model_utils import Entity
from backend.core.models import PokePokemon
from backend.core.schemas import FsPokemon
from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from firebase_admin import firestore
from pydantic import BaseModel

_DEFAULT_BATCH_SIZE = 100


_EntityModelType = TypeVar("_EntityModelType", bound=Entity)
_PydanticModelType = TypeVar("_PydanticModelType", bound=BaseModel)


class FirestoreModelSync(BaseModel, Generic[_EntityModelType, _PydanticModelType]):
    batch_size: int = _DEFAULT_BATCH_SIZE
    firestore_collection: str
    get_queryset: Callable[[], models.QuerySet[_EntityModelType]]
    get_key: Callable[[_EntityModelType], str]
    map_schema: Callable[[_EntityModelType], _PydanticModelType]

    def run(self):
        sync_timestamp = timezone.now()

        queryset = self.get_queryset()
        queryset.filter(modified_lte=sync_timestamp)

        paginator = Paginator(queryset, _DEFAULT_BATCH_SIZE)

        store = firestore.client()

        for i in paginator.page_range:
            batch = store.batch()
            page = paginator.page(i)

            for entity in page:
                batch.set(
                    store.document(
                        "{}{}".format(
                            self.firestore_collection,
                            self.get_key(entity),
                        ),
                    ),
                    self.map_schema(entity).dict(),
                )

            batch.commit()
