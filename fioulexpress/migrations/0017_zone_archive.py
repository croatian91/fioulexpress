# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-05 11:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fioulexpress", "0016_zone_actif"),
    ]

    operations = [
        migrations.AddField(
            model_name="zone",
            name="archive",
            field=models.BooleanField(default=False),
        ),
    ]
