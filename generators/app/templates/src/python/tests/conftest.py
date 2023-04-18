import pytest
from backend.contrib.tasks.tasks_emulator import patch_tasks_emulator
from tests import factories


@pytest.fixture(scope="session", autouse=True)
def tasks_emulator(request):
    # Patch the tasks module to use a local, in-process Cloud Tasks emulator in
    # development
    patch_tasks_emulator()


@pytest.fixture
def fs_user_profile_factory():
    """Generate fake Firestore user profile documents."""
    return factories.FirestoreUserProfileFactory


@pytest.fixture
def user_profile_factory():
    """Generate database user profile model instances."""
    return factories.EndUserFactory


@pytest.fixture
def poke_pokemon_factory():
    """Generate database user profile model instances."""
    return factories.PokePokemonWithTypesFactory
