import pytest
from backend.core.schemas import PokeDescriptorIn


@pytest.mark.parametrize(
    ["test_input", "expected"],
    [
        ("https://pokeapi.co/api/v2/generation/3/", "3"),
        ("https://pokeapi.co/api/v2/language/9/", "9"),
        ("https://pokeapi.co/api/v2/type/", None),
        ("", None),
    ],
)
def test_descriptor_in_get_api_entity_id(test_input: str, expected: int | None):
    desc = PokeDescriptorIn(name="test", url=test_input)
    assert desc.get_api_entity_id() == expected
