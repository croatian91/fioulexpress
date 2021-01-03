from django.contrib import admin
from django.forms.widgets import Textarea

# from sorl.thumbnail.admin import AdminImageMixin
from markdownx.widgets import AdminMarkdownxWidget
from markdownx.admin import MarkdownxModelAdmin


from .models import *


class ActualiteAdmin(admin.ModelAdmin):
    list_display = ["titre", "date"]
    prepopulated_fields = {
        "url": ("titre",),
    }
    fieldsets = (
        (None, {"fields": ("titre", "url", "date", "image_principale", "contenu")}),
        (
            "Options SEO",
            {
                "classes": ("collapse",),
                "fields": ("seo_title", "seo_description"),
            },
        ),
    )
    formfield_overrides = {
        models.TextField: {"widget": AdminMarkdownxWidget},
    }


admin.site.register(Actualite, ActualiteAdmin)


class PageAdmin(admin.ModelAdmin):
    list_display = ["titre", "adresse"]
    prepopulated_fields = {
        "adresse": ("titre",),
    }
    fieldsets = (
        (None, {"fields": ("titre", "adresse", "contenu")}),
        (
            "Options SEO",
            {
                "classes": ("collapse",),
                "fields": ("seo_title", "seo_description"),
            },
        ),
    )
    formfield_overrides = {
        models.TextField: {"widget": AdminMarkdownxWidget},
    }


admin.site.register(Page, PageAdmin)


class BlocAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
    ]
    list_search = [
        "nom",
    ]


admin.site.register(Bloc, BlocAdmin)

# Register your models here.
