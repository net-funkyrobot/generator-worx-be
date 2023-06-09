# Generated by Django 3.2.18 on 2023-04-01 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('l10n', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='name',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AddConstraint(
            model_name='name',
            constraint=models.UniqueConstraint(fields=('name', 'language'), name='unique_for_name_language'),
        ),
    ]
