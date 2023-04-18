import pytest


@pytest.mark.django_db
def test_pokemon_factories(poke_pokemon_factory):
    p1 = poke_pokemon_factory(name="Bulbasaur", poke_api_id=1)

    # Check l10n m2m names relation is being generated
    assert p1.names.all()[0].name.startswith("name_en")
    assert p1.species.names.all()[0].name.startswith("name_en")
    assert p1.species.color.names.all()[0].name.startswith("name_en")
    assert p1.species.habitat.names.all()[0].name.startswith("name_en")
    assert p1.types.all()[0].names.all()[0].name.startswith("name_en")
