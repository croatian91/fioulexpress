# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-08 05:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fioulexpress", "0010_auto_20160827_1151"),
    ]

    operations = [
        migrations.AddField(
            model_name="distributeur",
            name="actif",
            field=models.BooleanField(default=False),
        ),
    ]
