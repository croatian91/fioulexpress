from dal import autocomplete
from django.contrib.auth.models import User
from django.forms import ModelForm, inlineformset_factory, ChoiceField
from django import forms
from django.contrib import admin

from .models import *

class ZoneForm(ModelForm):
    class Meta:
        model = Zone
        fields = ['jours_livraison', 'types_paiement', 'nom', 'telephone', 'email', 'raison_sociale', 'siret', 'adresse', 'code_postal', 'ville']

DistribTarifFioulForm = inlineformset_factory(Zone, TarifFioul,
    exclude=('type_fioul',),
    extra=0,)

DistribTarifDecoteForm = inlineformset_factory(Zone, TarifDecote,
    exclude=('min', 'max',),
    extra=0,)

DistribTarifLivraisonForm = inlineformset_factory(Zone, TarifLivraison,
    exclude=('type_livraison',),
    extra=0,)


class AdresseForm(ModelForm):
    detail_4 = ChoiceField(label='Ville')
    class Meta:
        model = Adresse
        exclude = ['nom_adresse', 'pays', 'code_postal', 'client']

class AdresseFacturationForm(ModelForm):
    class Meta:
        model = Adresse
        exclude = ['nom_adresse', 'pays', 'client']

class ClientForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    class Meta:
        model = Client
        exclude = ['user']

class PanierForm(ModelForm):
    class Meta:
        model = Panier
        fields = ['commentaire', ]

class DistribCommandeForm(forms.Form):
    du = forms.DateField(label='Du (inclus)', widget=admin.widgets.AdminDateWidget)
    au = forms.DateField(label='Au (exclu)', widget=admin.widgets.AdminDateWidget)

class DistribDalForm(forms.ModelForm):
    distributeur = forms.ModelChoiceField(widget=autocomplete.ModelSelect2(url='distributeur-autocomplete'), queryset=Distributeur.objects.all())

    class Meta:
        model = Zone
        fields = ['distributeur', ]


class DistribZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        exclude = ['distributeur']
