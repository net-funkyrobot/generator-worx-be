from logging import getLogger

from backend.contrib.tasks import defer
from django.db.models import QuerySet
from django.http import HttpResponse
from structlog.stdlib import get_logger

from .models import PokePokemon
from .schemas import FsPokemon
from .services.dummy import DummyBackgroundTask
from .services.firestore_sync import FirestoreModelSync

_logger = get_logger(__name__)
_core_logger = getLogger(__name__)


def dummy_task(request):
    _logger.error("Hello world!")
    _core_logger.error("Hello Python!")
    return HttpResponse("OK")


def dummy_defer_task(request):
    _logger.error("Hello world!")
    _core_logger.error("Hello Python!")
    t = DummyBackgroundTask(some_param=1)
    defer(t)

    return HttpResponse("OK")


def _get_pokemon_queryset() -> QuerySet[PokePokemon]:
    return (
        PokePokemon.objects.select_related(
            "species__growth_rate",
            "species__color",
            "species__habitat",
        )
        .prefetch_related(
            "species__names__language",
            "species__color__names__language",
            "species__habitat__names__language",
            "types__names__language",
        )
        .all()
    )


def _map_pokemon_to_schema(entity: PokePokemon) -> FsPokemon:
    return FsPokemon(
        name=entity.name,
        height=entity.height,
        weight=entity.weight,
        base_experience=entity.base_experience,
        base_happiness=entity.species.base_happiness,
        is_baby=entity.species.is_baby,
        is_legendary=entity.species.is_legendary,
        is_mythical=entity.species.is_mythical,
        species=entity.species.get_names_schema(),
        color=entity.species.color.get_names_schema(),
        habitat=entity.species.habitat.get_names_schema()
        if entity.species.habitat
        else None,
        types=[pokemon_type.get_names_schema() for pokemon_type in entity.types.all()],
    )


def sync_pokemon(request):
    defer(
        FirestoreModelSync[PokePokemon, FsPokemon](
            firestore_collection="pokemon",
            get_key=lambda entity: entity.name,
            get_queryset=_get_pokemon_queryset,
            map_schema=_map_pokemon_to_schema,
        )
    )

    return HttpResponse("OK")
