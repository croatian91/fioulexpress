# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-03 05:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fioulexpress", "0015_auto_20160920_0709"),
    ]

    operations = [
        migrations.AddField(
            model_name="zone",
            name="actif",
            field=models.BooleanField(default=True),
        ),
    ]
