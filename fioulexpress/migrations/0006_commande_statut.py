# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-31 10:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fioulexpress", "0005_auto_20160731_1137"),
    ]

    operations = [
        migrations.AddField(
            model_name="commande",
            name="statut",
            field=models.CharField(
                choices=[("0", "valid\xe9e"), ("1", "annul\xe9e")],
                default="0",
                max_length=2,
            ),
        ),
    ]
