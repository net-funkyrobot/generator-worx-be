from uuid import uuid4

import factory
from backend.core.schemas import FsUserProfile
from django.utils.timezone import datetime

factory.Faker._DEFAULT_LOCALE = "en_GB"


class FirestoreUserProfileFactory(factory.Factory):
    email = factory.Sequence(
        lambda n: "testing+userprofile{0}@startupworx.net".format(n)
    )
    created = factory.Faker(
        "date_time_between",
        start_date=datetime(2022, 4, 20),
    )

    class Meta:
        model = FsUserProfile


class EndUserFactory(factory.django.DjangoModelFactory):
    uid = factory.Sequence(lambda n: "{0}".format(n))
    email = factory.Sequence(
        lambda n: "testing+userprofile{0}@startupworx.net".format(n)
    )

    class Meta:
        model = "core.EndUser"
        django_get_or_create = (
            "uid",
            "email",
        )


class EntityMixin:
    id = uuid4()


class LanguageFactory(EntityMixin, factory.django.DjangoModelFactory):
    name = "en"

    class Meta:
        model = "l10n.Language"
        django_get_or_create = ("name",)


class NameFactory(EntityMixin, factory.django.DjangoModelFactory):
    name = factory.LazyAttributeSequence(
        lambda obj, n: "name_{}_{}".format(obj.language.name, n)
    )
    language = factory.SubFactory(LanguageFactory)

    class Meta:
        model = "l10n.Name"
        django_get_or_create = ("name", "language")


def _create_names_m2m(created, extracted, obj, languages=("en", "fr", "it", "es")):
    if created and extracted:
        for name in extracted:
            obj.names.add(name)
    elif created:
        for i in range(len(languages)):
            obj.names.add(NameFactory(language=LanguageFactory(name=languages[i])))


class PokeGrowthRateFactory(EntityMixin, factory.django.DjangoModelFactory):
    poke_api_id = factory.Sequence(str)
    name = "slow"
    formula = "\\frac{5x^3}{4}"
    levels = [{"level": 100, "experience": 1250000}]

    class Meta:
        model = "core.PokeGrowthRate"
        django_get_or_create = ("name",)


class PokeColorFactory(EntityMixin, factory.django.DjangoModelFactory):
    poke_api_id = factory.Sequence(str)
    name = factory.sequence(lambda n: "color_{}".format(n))

    @factory.post_generation
    def names(self, created, extracted, *args, **kwargs):
        _create_names_m2m(created, extracted, self, *args, **kwargs)

    class Meta:
        model = "core.PokeColor"
        django_get_or_create = ("name",)


class PokeHabitatFactory(EntityMixin, factory.django.DjangoModelFactory):
    poke_api_id = factory.Sequence(str)
    name = factory.sequence(lambda n: "habitat_{}".format(n))

    @factory.post_generation
    def names(self, created, extracted, *args, **kwargs):
        _create_names_m2m(created, extracted, self, *args, **kwargs)

    class Meta:
        model = "core.PokeHabitat"
        django_get_or_create = ("name",)


class PokeTypeFactory(EntityMixin, factory.django.DjangoModelFactory):
    poke_api_id = factory.Sequence(str)
    name = factory.sequence(lambda n: "type_{}".format(n))

    @factory.post_generation
    def names(self, created, extracted, *args, **kwargs):
        _create_names_m2m(created, extracted, self, *args, **kwargs)

    class Meta:
        model = "core.PokeType"
        django_get_or_create = ("name",)


class PokeSpeciesFactory(EntityMixin, factory.django.DjangoModelFactory):
    poke_api_id = factory.Sequence(str)
    name = factory.sequence(lambda n: "species_{}".format(n))
    base_happiness = 100
    is_baby = False
    is_legendary = False
    is_mythical = False
    growth_rate = factory.SubFactory(PokeGrowthRateFactory)
    color = factory.SubFactory(PokeColorFactory)
    habitat = factory.SubFactory(PokeHabitatFactory)

    @factory.post_generation
    def names(self, created, extracted, *args, **kwargs):
        _create_names_m2m(created, extracted, self, *args, **kwargs)

    class Meta:
        model = "core.PokeSpecies"
        django_get_or_create = ("name",)


class PokePokemonFactory(EntityMixin, factory.django.DjangoModelFactory):
    poke_api_id = factory.Sequence(str)
    name = factory.sequence(lambda n: "pokemon_{}".format(n))
    base_experience = 20
    height = 100
    weight = 100
    species = factory.SubFactory(PokeSpeciesFactory)

    @factory.post_generation
    def names(self, created, extracted, *args, **kwargs):
        _create_names_m2m(created, extracted, self, *args, **kwargs)

    class Meta:
        model = "core.PokePokemon"
        django_get_or_create = ("name",)


class PokeTypeSlotFactory(EntityMixin, factory.django.DjangoModelFactory):
    type = factory.SubFactory(PokeTypeFactory)
    pokemon = factory.SubFactory(PokePokemonFactory)
    slot = 0

    class Meta:
        model = "core.PokeTypeSlot"


class PokePokemonWithTypesFactory(PokePokemonFactory):
    type1 = factory.RelatedFactory(
        PokeTypeSlotFactory,
        factory_related_name="pokemon",
        slot=1,
    )
    type1 = factory.RelatedFactory(
        PokeTypeSlotFactory,
        factory_related_name="pokemon",
        slot=2,
    )
