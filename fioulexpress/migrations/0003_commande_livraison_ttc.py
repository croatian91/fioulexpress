# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-31 08:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fioulexpress', '0002_prospect'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='livraison_ttc',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
    ]
