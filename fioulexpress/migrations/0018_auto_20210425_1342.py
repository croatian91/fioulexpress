# Generated by Django 3.1.5 on 2021-04-25 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fioulexpress", "0017_zone_archive"),
    ]

    operations = [
        migrations.AddField(
            model_name="typefioul",
            name="tooltip",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="config",
            name="meta_img",
            field=models.ImageField(blank=True, null=True, upload_to=""),
        ),
    ]
