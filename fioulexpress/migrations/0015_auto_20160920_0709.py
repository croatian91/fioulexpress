# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-20 05:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fioulexpress", "0014_auto_20160918_1635"),
    ]

    operations = [
        migrations.AlterField(
            model_name="commande",
            name="statut",
            field=models.CharField(
                choices=[("0", "valid\xe9e"), ("1", "annul\xe9e"), ("2", "en attente")],
                default="0",
                max_length=2,
            ),
        ),
    ]
