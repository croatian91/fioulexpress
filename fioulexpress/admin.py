# -*- coding: utf-8 -*-
import import_export
import tablib
from dal import autocomplete
from django import forms
from django.contrib import admin
from django.contrib.auth import login
from django.db.models import F
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.results import RowResult

from .models import *

# Register your models here.

# class ActualiteAdmin(admin.ModelAdmin):
#     pass
# admin.site.register(Actualite, ActualiteAdmin)


class CodePostalResource(resources.ModelResource):
    def import_row(self, row, instance_loader, dry_run=False, **kwargs):
        if dry_run:
            if row.get("zone__distributeur__nom", False) and row.get(
                "zone__nom", False
            ):
                result = super(CodePostalResource, self).import_row(
                    row, instance_loader, dry_run=False, **kwargs
                )
                instance = CodePostal.objects.get(id=result.object_id)
                if (result.import_type != result.IMPORT_TYPE_NEW) and (
                    not (instance.zone) or instance.zone.nom != row.get("zone__nom")
                ):
                    result.diff[2] = "%s" % row.get("zone__distributeur__nom", False)
                    result.diff[3] = "%s" % row.get("zone__nom", False)
                    result.import_type = result.IMPORT_TYPE_UPDATE
                    return result
        else:
            if row.get("zone__distributeur__nom", False) and row.get(
                "zone__nom", False
            ):
                distributeur, created = Distributeur.objects.get_or_create(
                    nom=row.get("zone__distributeur__nom")
                )
                if row.get("zone__nom", False):
                    zone, created = Zone.objects.get_or_create(
                        distributeur=distributeur, nom=row.get("zone__nom")
                    )
                    result = super(CodePostalResource, self).import_row(
                        row, instance_loader, dry_run=False, **kwargs
                    )
                    instance = CodePostal.objects.get(id=result.object_id)
                    if instance.zone != zone:
                        instance.zone = zone
                        if result.import_type != result.IMPORT_TYPE_NEW:
                            result.import_type = result.IMPORT_TYPE_UPDATE
                        instance.save()
                        return result
        row_result = self.get_row_result_class()()
        row_result.import_type = RowResult.IMPORT_TYPE_SKIP
        row_result.diff = self.get_diff(None, None, dry_run)
        return row_result

    class Meta:
        model = CodePostal
        fields = ("code_postal", "commune", "zone__distributeur__nom", "zone__nom")
        import_id_fields = ("code_postal", "commune")
        skip_unchanged = True


class ZoneResource(resources.ModelResource):
    def import_row(self, row, instance_loader, dry_run=False, **kwargs):

        row_result = self.get_row_result_class()()
        row_result.import_type = RowResult.IMPORT_TYPE_SKIP
        row_result.diff = self.get_diff(None, None, dry_run)

        if dry_run:
            if row.get("distributeur__nom", False) and row.get("nom", False):
                distribs = Distributeur.objects.filter(nom=row.get("distributeur__nom"))
                if distribs:
                    zones = Zone.objects.filter(
                        nom=row.get("nom"),
                        distributeur__nom=row.get("distributeur__nom"),
                    )
                    if zones:
                        row_result.import_type = RowResult.IMPORT_TYPE_UPDATE
                        row_result.object_repr = force_str(zones[0])
                        row_result.object_id = zones[0].id
                        row_result.diff = self.get_diff(zones[0], zones[0], dry_run)
                    else:
                        row_result.import_type = RowResult.IMPORT_TYPE_NEW
                        zone = Zone(
                            nom=row.get("nom"),
                            email=row.get("email"),
                            telephone=row.get("telephone"),
                        )
                        row_result.diff = self.get_diff(zone, zone, dry_run)
        else:
            if row.get("distributeur__nom", False) and row.get("nom", False):
                RowResult.IMPORT_TYPE_UPDATE

                distrib, created = Distributeur.objects.get_or_create(
                    nom=row.get("distributeur__nom")
                )
                if not distrib.user:
                    distrib.user = User.objects.create(username=distrib.nom)
                    distrib.user.set_password("Fioul%Express")
                    distrib.user.is_staff = True
                    distrib.user.groups.add(1)
                    distrib.user.save()
                    distrib.save()

                zone, created = distrib.zone_set.get_or_create(nom=row.get("nom"))
                if created:
                    row_result.import_type = RowResult.IMPORT_TYPE_NEW
                zone.email = row.get("email")
                zone.telephone = row.get("telephone")

                jours = []
                if row.get("lundi", False) == "1":
                    jours.append("0")
                if row.get("mardi", False) == "1":
                    jours.append("1")
                if row.get("mercredi", False) == "1":
                    jours.append("2")
                if row.get("jeudi", False) == "1":
                    jours.append("3")
                if row.get("vendredi", False) == "1":
                    jours.append("4")
                if row.get("samedi", False) == "1":
                    jours.append("5")
                if row.get("dimanche", False) == "1":
                    jours.append("6")
                zone.jours_livraison = jours

                types_paiement = []
                if row.get("paiement_cheque", False) == "1":
                    types_paiement.append("0")
                if row.get("paiement_espece", False) == "1":
                    types_paiement.append("1")
                if row.get("paiement_cb", False) == "1":
                    types_paiement.append("2")
                zone.types_paiement = types_paiement

                zone.save()

                tarif_fioul, created = zone.tariffioul_set.get_or_create(
                    type_fioul_id=2
                )
                tarif_fioul.prix_ttc = Decimal(row.get("prix_ordinaire", False) or 0)
                tarif_fioul.actif = tarif_fioul.prix_ttc != Decimal(0)
                tarif_fioul.save()

                tarif_fioul, created = zone.tariffioul_set.get_or_create(
                    type_fioul_id=3
                )
                tarif_fioul.prix_ttc = Decimal(row.get("prix_superieur", False) or 0)
                tarif_fioul.actif = tarif_fioul.prix_ttc != Decimal(0)
                tarif_fioul.save()

                tarif_fioul, created = zone.tariffioul_set.get_or_create(
                    type_fioul_id=4
                )
                tarif_fioul.prix_ttc = Decimal(row.get("prix_gnr", False) or 0)
                tarif_fioul.actif = tarif_fioul.prix_ttc != Decimal(0)
                tarif_fioul.save()

                tarif_fioul, created = zone.tariffioul_set.get_or_create(
                    type_fioul_id=5
                )
                tarif_fioul.prix_ttc = Decimal(
                    row.get("prix_gnr_superieur", False) or 0
                )
                tarif_fioul.actif = tarif_fioul.prix_ttc != Decimal(0)
                tarif_fioul.save()

                tarif_fioul, created = zone.tariffioul_set.get_or_create(
                    type_fioul_id=1
                )
                tarif_fioul.prix_ttc = Decimal(row.get("prix_cristal", False) or 0)
                tarif_fioul.actif = tarif_fioul.prix_ttc != Decimal(0)
                tarif_fioul.save()

                tarif_decote, created = zone.tarifdecote_set.get_or_create(
                    min=500, max=999
                )
                tarif_decote.decote = Decimal(row.get("decote_1", False) or 0)
                tarif_decote.save()

                tarif_decote, created = zone.tarifdecote_set.get_or_create(
                    min=1000, max=2999
                )
                tarif_decote.decote = Decimal(row.get("decote_2", False) or 0)
                tarif_decote.save()

                tarif_decote, created = zone.tarifdecote_set.get_or_create(
                    min=3000, max=3999
                )
                tarif_decote.decote = Decimal(row.get("decote_3", False) or 0)
                tarif_decote.save()

                tarif_decote, created = zone.tarifdecote_set.get_or_create(
                    min=4000, max=10000
                )
                tarif_decote.decote = Decimal(row.get("decote_4", False) or 0)
                tarif_decote.save()

                tarif_livraison, created = zone.tariflivraison_set.get_or_create(
                    type_livraison_id=2
                )
                tarif_livraison.actif = True
                tarif_livraison.extra = 0
                tarif_livraison.save()

                tarif_livraison, created = zone.tariflivraison_set.get_or_create(
                    type_livraison_id=1
                )
                if row.get("livraison_express", False) == "null":
                    tarif_livraison.extra = Decimal(0)
                    tarif_livraison.actif = False
                else:
                    tarif_livraison.extra = Decimal(
                        row.get("livraison_express", False) or 0
                    )
                    tarif_livraison.actif = True
                tarif_livraison.save()

                tarif_livraison, created = zone.tariflivraison_set.get_or_create(
                    type_livraison_id=3
                )
                if row.get("livraison_eco", False) == "null":
                    tarif_livraison.extra = Decimal(0)
                    tarif_livraison.actif = False
                else:
                    tarif_livraison.extra = Decimal(
                        row.get("livraison_eco", False) or 0
                    )
                    tarif_livraison.actif = True
                tarif_livraison.save()

        return row_result

    class Meta:
        model = Zone
        fields = ["nom", "distributeur__nom", "email", "telephone"]
        import_id_fields = [
            "nom",
        ]


class CodePostalAdmin(ImportExportModelAdmin):
    verbose_name_plural = "Code Postaux"
    resource_class = CodePostalResource
    list_display = ["__str__", "zone"]
    list_filter = ["zone"]
    search_fields = ["code_postal", "commune"]


admin.site.register(CodePostal, CodePostalAdmin)


class ConfigAdmin(admin.ModelAdmin):
    list_display = ["nom", "commission", "heure_limite_livraison", "actif"]


admin.site.register(Config, ConfigAdmin)


class JourFerieAdmin(admin.ModelAdmin):
    list_filter = ["date"]


admin.site.register(JourFerie, JourFerieAdmin)


class TypeMessageAdmin(admin.ModelAdmin):
    pass


admin.site.register(TypeMessage, TypeMessageAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ["__str__", "a_envoyer", "envoye", "type"]
    search_fields = ["destinataire", "data"]


admin.site.register(Message, MessageAdmin)


class TarifLivraisonInline(admin.TabularInline):
    model = TarifLivraison
    extra = 0


class TarifFioulInline(admin.TabularInline):
    model = TarifFioul
    extra = 0


class TarifDecoteInline(admin.TabularInline):
    model = TarifDecote
    extra = 0


class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 0


def se_connecter_distrib(modeladmin, request, queryset):
    if request.user.is_superuser:
        for d in queryset:
            u = d.user
            u.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, u)
            return redirect("/distributeur/")


se_connecter_distrib.short_description = "Se connecter avec le distributeur sélectionné"


class DistributeurAdmin(admin.ModelAdmin):
    actions = [se_connecter_distrib]
    list_display = ["nom", "actif", "admin_se_connecter_distributeur"]
    list_editable = ["actif"]
    list_filter = ["actif"]
    # inlines = [ZoneInline, TarifLivraisonInline, TarifFioulInline]

    def admin_se_connecter_distributeur(self, instance):
        return format_html(
            '<a href="%s" target="_blank">Se connecter</a>'
            % reverse("se-connecter-distrib", kwargs={"id_distributeur": instance.id})
        )

    admin_se_connecter_distributeur.allow_tags = True
    admin_se_connecter_distributeur.short_description = ""


admin.site.register(Distributeur, DistributeurAdmin)


class DistributeurResource(resources.ModelResource):
    def import_data(self, dataset, dry_run=False, raise_errors=False):
        pass

    class Meta:
        model = Distributeur


# class TarifLivraisonAdmin(admin.ModelAdmin):
#    pass
# admin.site.register(TarifLivraison, TarifLivraisonAdmin)


class TypeFioulAdmin(admin.ModelAdmin):
    list_display = ["nom", "position"]


admin.site.register(TypeFioul, TypeFioulAdmin)


class TypeLivraisonAdmin(admin.ModelAdmin):
    list_display = ["nom", "position"]


admin.site.register(TypeLivraison, TypeLivraisonAdmin)


class CodePostalInline(admin.TabularInline):
    model = CodePostal


class ZoneAdminForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = "__all__"
        widgets = {
            "distributeur": autocomplete.ModelSelect2(url="distributeur-autocomplete"),
            "tarifs": autocomplete.ModelSelect2Multiple(url="typetarif-autocomplete"),
        }


class ZoneAdmin(ImportExportModelAdmin):
    # inlines = [CodePostalInline]
    inlines = [
        TarifFioulInline,
        TarifDecoteInline,
        TarifLivraisonInline,
    ]
    resource_class = ZoneResource
    form = ZoneAdminForm
    search_fields = ["nom", "distributeur__nom", "codepostal__code_postal"]
    list_display = ["nom", "actif", "archive"]
    list_filter = ["actif", "distributeur"]
    list_editable = ["actif", "archive"]


admin.site.register(Zone, ZoneAdmin)


class AdresseInline(admin.StackedInline):
    model = Adresse
    extra = 0


class ClientResource(resources.ModelResource):
    def export(self, queryset=None, *args, **kwargs):
        headers = ["prenom", "nom", "email"]
        queryset = (
            Client.objects.filter(adresse__nom_adresse="adresse_par_defaut")
            .annotate(
                prenom=F("adresse__prenom"),
                nom=F("adresse__nom"),
            )
            .select_related("adresse")
            .values(*headers)
        )
        data = tablib.Dataset(headers=headers)

        for o in queryset:
            row = [o[k] for k in headers]
            data.append(row)

        return data

    class Meta:
        model = Client
        fields = (
            "prenom",
            "nom",
            "email",
        )


class ClientAdmin(ImportExportModelAdmin):
    inlines = [
        AdresseInline,
    ]
    search_fields = ["email", "adresse__nom", "adresse__prenom"]
    resource_class = ClientResource


admin.site.register(Client, ClientAdmin)


class CommandeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "client_nom",
        "type_fioul",
        "type_livraison",
        "date_livraison",
        "statut",
        "total_ttc",
        "commission_ttc",
    ]
    list_filter = ["zone__distributeur", "type_fioul", "type_livraison", "date"]


# admin.site.register(Commande, CommandeAdmin)


class PanierAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "type_fioul",
        "type_livraison",
        "client",
    ]


# admin.site.register(Panier, PanierAdmin)


class ProspectAdmin(admin.ModelAdmin):
    list_display = ["email", "code_postal", "date"]


admin.site.register(Prospect, ProspectAdmin)
