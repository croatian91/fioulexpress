# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-29 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fioulexpress', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prospect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('code_postal', models.CharField(max_length=10, verbose_name='Code postal')),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
