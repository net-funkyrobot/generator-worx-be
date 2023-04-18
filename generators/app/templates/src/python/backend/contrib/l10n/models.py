from django.db import models

from ..model_utils import Entity
from .schemas import FsNames


class NamesMixin(models.Model):
    name = models.CharField(max_length=255, unique=True)
    names = models.ManyToManyField("l10n.Name")

    def get_names_schema(self):
        names = self.names.all()
        en = names[0].name

        l10n = {}
        for name in names:
            if name.language.name == "en":
                en = name.name
            l10n[name.language.name] = name.name

        return FsNames(en=en, l10n=l10n)

    class Meta:
        abstract = True


class Language(Entity):
    name = models.CharField(max_length=10, unique=True)


class Name(Entity):
    name = models.CharField(max_length=255, db_index=True)
    language = models.ForeignKey(
        "l10n.Language",
        on_delete=models.CASCADE,
        related_name="lexicon",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("name", "language"),
                name="unique_for_name_language",
            )
        ]
