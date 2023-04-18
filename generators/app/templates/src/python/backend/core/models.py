from backend.contrib.l10n.models import NamesMixin
from backend.contrib.model_utils import Entity
from django.db import models

FIRESTORE_STRING_MAX_LENGTH = 128


class PokeApiMixin(models.Model):
    poke_api_id = models.CharField(max_length=10, unique=True)

    class Meta:
        abstract = True


class PokeColor(PokeApiMixin, NamesMixin, Entity):
    pass


class PokeGrowthRate(PokeApiMixin, Entity):
    name = models.CharField(max_length=255, unique=True)
    formula = models.CharField(max_length=255)
    levels = models.JSONField()


class PokeHabitat(PokeApiMixin, NamesMixin, Entity):
    pass


class PokeSpecies(PokeApiMixin, NamesMixin, Entity):
    base_happiness = models.IntegerField()
    is_baby = models.BooleanField()
    is_legendary = models.BooleanField()
    is_mythical = models.BooleanField()
    growth_rate = models.ForeignKey(PokeGrowthRate, on_delete=models.CASCADE)
    color = models.ForeignKey(PokeColor, on_delete=models.CASCADE)
    habitat = models.ForeignKey(
        PokeHabitat,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )


class PokeType(PokeApiMixin, NamesMixin, Entity):
    pass


class PokePokemon(PokeApiMixin, NamesMixin, Entity):
    base_experience = models.IntegerField()
    height = models.IntegerField()
    weight = models.IntegerField()
    species = models.ForeignKey(PokeSpecies, on_delete=models.CASCADE)
    types = models.ManyToManyField(PokeType, through="core.PokeTypeSlot")


class PokeTypeSlot(Entity):
    type = models.ForeignKey(PokeType, on_delete=models.CASCADE)
    pokemon = models.ForeignKey(PokePokemon, on_delete=models.CASCADE)
    slot = models.IntegerField(db_index=True)

    class Meta:
        ordering = ["slot"]


class EndUser(Entity):
    firebase_auth_id = models.CharField(
        max_length=FIRESTORE_STRING_MAX_LENGTH,
        unique=True,
        help_text="Firebase Auth User ID",
    )
    email = models.EmailField(db_index=True)
    opt_in_communications = models.BooleanField(
        default=False,
        help_text="User consent for email and push notification communications",
    )
    mailing_list_subscribed = models.BooleanField(
        default=False,
        help_text="Marks if the user has been subscribed to the mailing list",
    )
    mailing_list_has_unsubscribed = models.BooleanField(
        default=False,
        help_text="Marks if the user has unsubscribed themselves to the mailing "
        "list (we shouldn't subsequently re-add them).",
    )
    mailing_list_id = models.CharField(max_length=30, blank=True, null=True)
