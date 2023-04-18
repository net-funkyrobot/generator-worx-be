import re
from datetime import datetime
from typing import List, Optional

from backend.contrib.l10n.schemas import FsNames
from pydantic import BaseModel, EmailStr


class FsUserProfile(BaseModel):
    email: EmailStr
    created: datetime
    opt_in_communications: bool


class FsPokemon(BaseModel):
    name: str
    height: int
    weight: int
    base_experience: int
    base_happiness: int
    is_baby: bool
    is_legendary: bool
    is_mythical: bool
    species: FsNames
    color: FsNames
    habitat: Optional[FsNames]
    types: List[FsNames]


class PokeDescriptorIn(BaseModel):
    name: str
    url: str

    def get_api_entity_id(self):
        match_obj = re.search(r"([-\w]+)\/(\d+)\/$", self.url)
        return match_obj.group(2) if match_obj else None


class PokeNameIn(BaseModel):
    name: str
    language: PokeDescriptorIn


class PokeNamedResourceIn(BaseModel):
    id: int
    name: str
    names: list[PokeNameIn]


class PokeVarietyDescriptorIn(BaseModel):
    is_default: bool
    pokemon: PokeDescriptorIn


class PokeSpeciesIn(BaseModel):
    id: int
    name: str
    base_happiness: int
    is_baby: bool
    is_legendary: bool
    is_mythical: bool
    color: PokeDescriptorIn
    habitat: PokeDescriptorIn
    growth_rate: PokeDescriptorIn
    names: list[PokeNameIn]
    varieties: list[PokeVarietyDescriptorIn]


class PokeLevelIn(BaseModel):
    level: int
    experience: int


class PokeGrowthRateIn(BaseModel):
    id: int
    name: str
    formula: str
    levels: list[PokeLevelIn]


class PokeTypeSlotIn(BaseModel):
    slot: int
    type: PokeDescriptorIn


class PokePokemonIn(BaseModel):
    id: int
    name: str
    base_experience: int
    height: int
    weight: int
    types: list[PokeTypeSlotIn]
    species: PokeDescriptorIn


class PokeGenerationIn(BaseModel):
    id: int
    name: str
    names: list[PokeNameIn]
    pokemon_species: list[PokeDescriptorIn]
    types: list[PokeDescriptorIn]
