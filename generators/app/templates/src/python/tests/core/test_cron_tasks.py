from unittest.mock import patch

import pytest
from backend.core.cron_tasks import (
    _get_pokemon_queryset,
    _map_pokemon_to_schema,
    sync_pokemon,
)
from django.test import RequestFactory
from django.urls import reverse


@pytest.mark.django_db
def test_pokemon_queryset_mapper(django_assert_num_queries, poke_pokemon_factory):
    poke_pokemon_factory(name="bulbasaur")
    poke_pokemon_factory(name="charmander")

    with django_assert_num_queries(10):
        queryset = _get_pokemon_queryset()
        entity = queryset.first()
        assert entity
        schema = _map_pokemon_to_schema(entity)

    assert schema.name == entity.name
    assert schema.height == entity.height
    assert schema.weight == entity.weight
    assert schema.base_experience == entity.base_experience
    assert schema.base_happiness == entity.species.base_happiness
    assert schema.is_baby == entity.species.is_baby
    assert schema.is_legendary == entity.species.is_legendary
    assert schema.is_mythical == entity.species.is_mythical

    assert schema.species.en == entity.species.names.all()[0].name
    for i, (lang, name) in enumerate(schema.species.l10n.items()):
        assert name == entity.species.names.all()[i].name
        assert lang == entity.species.names.all()[i].language.name

    assert schema.color.en == entity.species.color.names.all()[0].name
    for i, (lang, name) in enumerate(schema.color.l10n.items()):
        assert name == entity.species.color.names.all()[i].name
        assert lang == entity.species.color.names.all()[i].language.name

    if entity.species.habitat:
        assert schema.habitat
        assert schema.habitat.en == entity.species.habitat.names.all()[0].name
        for i, (lang, name) in enumerate(schema.habitat.l10n.items()):
            assert name == entity.species.habitat.names.all()[i].name
            assert lang == entity.species.habitat.names.all()[i].language.name

    for i, type in enumerate(schema.types):
        assert schema.types[i].en == entity.types.all()[0].names.all()[0].name
        for j, (lang, name) in enumerate(type.l10n.items()):
            assert name == entity.types.all()[i].names.all()[j].name
            assert lang == entity.types.all()[i].names.all()[j].language.name


def test_sync_pokemon(rf: RequestFactory):
    with patch("backend.core.cron_tasks.defer") as mock_defer:
        sync_pokemon(rf.get(reverse("tasks:sync-pokemon")))
        mock_defer.assert_called_once()
