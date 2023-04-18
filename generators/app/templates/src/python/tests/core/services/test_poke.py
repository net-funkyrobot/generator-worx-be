from typing import Type
from unittest.mock import patch

import pytest
from backend.contrib.l10n.models import Language, Name
from backend.core.models import (
    PokeColor,
    PokeGrowthRate,
    PokeHabitat,
    PokePokemon,
    PokeSpecies,
)
from backend.core.schemas import (
    PokeDescriptorIn,
    PokeGenerationIn,
    PokeGrowthRateIn,
    PokeNamedResourceIn,
    PokeNameIn,
    PokePokemonIn,
    PokeSpeciesIn,
)
from backend.core.services.poke import (
    PokeSpeciesSync,
    PokeSync,
    _create_and_add_names,
    _fetch_entity,
)
from ninja import Schema


@pytest.mark.django_db
def test_create_and_add_names():
    existing_language = Language.objects.create(name="en")
    Name.objects.create(name="Purple", language=existing_language)

    names = [
        PokeNameIn(name="Purple", language=PokeDescriptorIn(name="en", url="")),
        PokeNameIn(name="Violet", language=PokeDescriptorIn(name="fr", url="")),
        PokeNameIn(name="Lila", language=PokeDescriptorIn(name="de", url="")),
    ]
    color = PokeColor.objects.create(poke_api_id="some-id", name="Purple")

    assert Language.objects.all().count() == 1
    assert Name.objects.all().count() == 1

    _create_and_add_names(color, names)

    assert Language.objects.all().count() == 3
    assert Name.objects.all().count() == 3
    assert set(Language.objects.values_list("name", flat=True)) == {"en", "fr", "de"}


@pytest.mark.vcr
@pytest.mark.parametrize(
    ["entity_url", "schema_class"],
    [
        ("https://pokeapi.co/api/v2/generation/1/", PokeGenerationIn),
        ("https://pokeapi.co/api/v2/pokemon-species/1/", PokeSpeciesIn),
        ("https://pokeapi.co/api/v2/pokemon-color/1/", PokeNamedResourceIn),
        ("https://pokeapi.co/api/v2/pokemon-habitat/1/", PokeNamedResourceIn),
        ("https://pokeapi.co/api/v2/growth-rate/1/", PokeGrowthRateIn),
        ("https://pokeapi.co/api/v2/pokemon/1/", PokePokemonIn),
    ],
)
def test_fetch_entity(entity_url: str, schema_class: Type[Schema]):
    _fetch_entity(entity_url, schema_class)


@pytest.mark.vcr
def test_poke_sync():
    with patch("backend.core.services.poke.defer") as mock_defer:
        PokeSync(generations_to_sync=["1"]).run()
        assert mock_defer.call_count == 151  # Gotta catch them all...

        for call_args in mock_defer.call_args_list:
            assert call_args.args[0].api_entity_url.startswith(
                "https://pokeapi.co/api/v2/pokemon-species/",
            )


@pytest.mark.django_db
@pytest.mark.vcr
def test_poke_species_sync():
    # Sync Bulbasaur species
    PokeSpeciesSync(
        api_entity_url="https://pokeapi.co/api/v2/pokemon-species/1/",
    ).run()

    assert PokeColor.objects.all().count() == 1
    color = PokeColor.objects.first()
    assert color and color.name == "green"

    assert PokeGrowthRate.objects.all().count() == 1
    growth_rate = PokeGrowthRate.objects.first()
    assert growth_rate
    assert growth_rate.name == "medium-slow"
    assert growth_rate.formula == "\\frac{6x^3}{5} - 15x^2 + 100x - 140"
    assert len(growth_rate.levels) > 0

    assert PokeHabitat.objects.all().count() == 1
    habitat = PokeHabitat.objects.first()
    assert habitat
    assert habitat.name == "grassland"

    assert PokeSpecies.objects.all().count() == 1
    species = PokeSpecies.objects.select_related(
        "color",
        "habitat",
        "growth_rate",
    ).first()
    assert species
    assert species.name == "bulbasaur"
    assert species.base_happiness == 50
    assert not species.is_baby
    assert not species.is_legendary
    assert not species.is_mythical
    assert species.color_id == color.id  # type: ignore
    assert species.habitat_id == habitat.id  # type: ignore

    assert PokePokemon.objects.all().count() == 1

    pokemon = PokePokemon.objects.first()
    assert pokemon
    assert pokemon.name == "bulbasaur"
    assert pokemon.base_experience == 64
    assert pokemon.height == 7
    assert pokemon.weight == 69
    assert pokemon.species_id == species.id  # type: ignore

    assert pokemon.types.all().count() == 2
    pokemon_types = pokemon.types.all()
    assert pokemon_types[0].name == "grass"
    assert pokemon_types[1].name == "poison"
