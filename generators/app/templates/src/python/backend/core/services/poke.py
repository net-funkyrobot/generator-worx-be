from typing import Type, TypeVar

import requests
from backend.contrib.l10n.models import Language, Name, NamesMixin
from backend.contrib.tasks import defer
from django.db import models
from pydantic import BaseModel

from ..models import (
    PokeColor,
    PokeGrowthRate,
    PokeHabitat,
    PokePokemon,
    PokeSpecies,
    PokeType,
)
from ..schemas import (
    PokeGenerationIn,
    PokeGrowthRateIn,
    PokeNamedResourceIn,
    PokeNameIn,
    PokePokemonIn,
    PokeSpeciesIn,
)

_PydanticModelType = TypeVar("_PydanticModelType", bound=BaseModel)

API_URL = "https://pokeapi.co/api/v2"


def _fetch_entity(
    entity_url: str, schema_class: Type[_PydanticModelType]
) -> _PydanticModelType:
    res = requests.get(entity_url)
    res.raise_for_status()
    return schema_class.parse_raw(res.text)


def _create_and_add_names(entity: models.Model, names: list[PokeNameIn]):
    if isinstance(entity, NamesMixin):
        for name in names:
            try:
                name_entity = Name.objects.get(name=name.name)
            except Name.DoesNotExist:
                language_entity, _ = Language.objects.get_or_create(
                    name=name.language.name,
                )
                name_entity, _ = Name.objects.get_or_create(
                    name=name.name,
                    defaults={"language": language_entity},
                )

            entity.names.add(name_entity)


class PokeSync(BaseModel):
    generations_to_sync: list[str]

    def run(self):
        for generation_name in self.generations_to_sync:
            generation = _fetch_entity(
                "{0}/generation/{1}/".format(API_URL, generation_name),
                PokeGenerationIn,
            )

            for desc in generation.pokemon_species:
                defer(PokeSpeciesSync(api_entity_url=desc.url))


class PokeSpeciesSync(BaseModel):
    api_entity_url: str

    def run(self):
        species = _fetch_entity(self.api_entity_url, PokeSpeciesIn)

        try:
            color_entity = PokeColor.objects.get(
                poke_api_id=species.color.get_api_entity_id()
            )
        except PokeColor.DoesNotExist:
            color = _fetch_entity(species.color.url, PokeNamedResourceIn)
            color_entity = PokeColor.objects.create(name=color.name)
            _create_and_add_names(color_entity, color.names)

        try:
            growth_rate_entity = PokeGrowthRate.objects.get(
                poke_api_id=species.growth_rate.get_api_entity_id()
            )
        except PokeGrowthRate.DoesNotExist:
            growth_rate = _fetch_entity(species.growth_rate.url, PokeGrowthRateIn)
            growth_rate_entity = PokeGrowthRate.objects.create(
                poke_api_id=growth_rate.id,
                name=growth_rate.name,
                formula=growth_rate.formula,
                levels=[level.json() for level in growth_rate.levels],
            )

        entity = PokeSpecies.objects.create(
            name=species.name,
            color=color_entity,
            growth_rate=growth_rate_entity,
            poke_api_id=species.id,
            base_happiness=species.base_happiness,
            is_baby=species.is_baby,
            is_legendary=species.is_legendary,
            is_mythical=species.is_mythical,
        )

        if species.habitat:
            try:
                entity.habitat = PokeHabitat.objects.get(
                    poke_api_id=species.habitat.get_api_entity_id()
                )
                entity.save()
            except PokeHabitat.DoesNotExist:
                habitat = _fetch_entity(species.habitat.url, PokeNamedResourceIn)
                entity.habitat = PokeHabitat.objects.create(
                    name=habitat.name,
                )
                entity.save()
                _create_and_add_names(entity.habitat, habitat.names)

        _create_and_add_names(entity, species.names)

        for pokemon_variety in species.varieties:
            pokemon = _fetch_entity(pokemon_variety.pokemon.url, PokePokemonIn)

            pokemon_entity = PokePokemon.objects.create(
                poke_api_id=pokemon.id,
                name=pokemon.name,
                species=entity,
                base_experience=pokemon.base_experience,
                height=pokemon.height,
                weight=pokemon.weight,
            )

            for type_slot in pokemon.types:
                try:
                    type_entity = PokeType.objects.get(
                        poke_api_id=type_slot.type.get_api_entity_id()
                    )
                except PokeType.DoesNotExist:
                    type = _fetch_entity(type_slot.type.url, PokeNamedResourceIn)
                    type_entity = PokeType.objects.create(
                        name=type.name,
                        poke_api_id=type.id,
                    )
                    _create_and_add_names(type_entity, type.names)

                pokemon_entity.types.add(
                    type_entity, through_defaults={"slot": type_slot.slot}
                )
