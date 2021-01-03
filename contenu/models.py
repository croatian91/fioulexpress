from __future__ import unicode_literals

from django.db import models

# from django.contrib.auth.models import User
# from multiselectfield import MultiSelectField
# from tinymce.models import HTMLField
# from ckeditor.fields import RichTextField, RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingField
from sorl.thumbnail import ImageField


class Actualite(models.Model):
    titre = models.CharField(max_length=100)
    url = models.SlugField(max_length=200)
    date = models.DateField()
    image_principale = ImageField(upload_to="actu")
    contenu = RichTextUploadingField(blank=True, null=True)
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.CharField(max_length=1000, blank=True, null=True)


class Page(models.Model):
    titre = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255, unique=True)
    contenu = models.TextField(blank=True, null=True)
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.CharField(max_length=1000, blank=True, null=True)


class Bloc(models.Model):
    nom = models.CharField(max_length=100)
    contenu = models.TextField(null=True, blank=True)
