"""fioul URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path

from contenu.views import *
from fioulexpress.views import *

urlpatterns = [
    re_path(r"^$", home),
    re_path(r"^markdownx/", include("markdownx.urls")),
    re_path(r"^ckeditor/", include("ckeditor_uploader.urls")),
    re_path(r"^admin/", admin.site.urls),
]

# Interface distributeur
urlpatterns += [
    re_path(
        r"^distributeur/commande/$",
        distrib_commandes,
        name="distrib-commandes",
    ),
    re_path(
        r"^distributeur/commande/(?P<id_commande>\d+)/annuler/$",
        distrib_commande_annuler,
        name="distrib-commande-annuler",
    ),
    re_path(
        r"^distributeur/commande/(?P<commande_id>\d+)/pdf/$",
        admin_commande_pdf,
        name="distrib-commande-pdf",
    ),
    re_path(
        r"^distributeur/commande/(?P<id_commande>\d+)/$",
        distrib_commande_detail,
        name="distrib-commande-detail",
    ),
    # re_path(
    #    r'^distributeur/inscription/$',
    #    distrib_inscription,
    #    name='distrib-inscription',
    # ),
    re_path(
        r"^distributeur/produits/$",
        distrib_produits,
        name="distrib-produits",
    ),
    re_path(
        r"^distributeur/livraisons/$",
        distrib_livraisons,
        name="distrib-livraisons",
    ),
    re_path(
        r"^distributeur/creer_zone/$",
        distrib_zone_add,
        name="distrib-zone-add",
    ),
    re_path(
        r"^distributeur/remove_cp/(?P<cp>.+)/$",
        distrib_remove_cp,
        name="distrib-remove-cp",
    ),
    re_path(
        r"^distributeur/import_cp/$",
        distrib_import_cp,
        name="distrib-import-cp",
    ),
    re_path(
        r"^distributeur/se_connecter_distrib/(?P<id_distributeur>\d+)/$",
        admin_se_connecter_distrib,
        name="se-connecter-distrib",
    ),
    re_path(
        r"^distributeur/$",
        distrib_hp,
        name="distrib-hp",
    ),
    re_path(r"^distributeur/", admin.site.urls, name="distrib-admin"),
]

# Interface client
urlpatterns += [
    re_path(
        r"^commande/valide_cp/$",
        client_valide_cp,
        name="client-valide-cp",
    ),
    re_path(
        r"^commande/devis/$",
        client_commande_devis,
        name="client-commande-devis",
    ),
    re_path(
        r"^commande/valoriser/$",
        client_commande_valoriser,
        name="client-commande-valoriser",
    ),
    re_path(
        r"^commande/livraison/$",
        client_commande_livraison,
        name="client-commande-livraison",
    ),
    re_path(
        r"^commande/paiement/$",
        client_commande_paiement,
        name="client-commande-paiement",
    ),
    re_path(
        r"^commande/confirmation/$",
        client_commande_confirmation,
        name="client-commande-confirmation",
    ),
    re_path(
        r"^commande/monetico_ok/$",
        client_commande_monetico_ok,
        name="client-commande-monetico-ok",
    ),
    re_path(
        r"^commande/monetico_ko/$",
        client_commande_monetico_ko,
        name="client-commande-monetico-ko",
    ),
    re_path(
        r"^client/connexion/$",
        client_connexion,
        name="client-connexion",
    ),
    re_path(
        r"^client/deconnexion/$",
        client_deconnexion,
        name="client-deconnexion",
    ),
    re_path(
        r"^client/motdepasse/$",
        client_recuperation_mot_passe,
        name="client-motdepasse",
    ),
    re_path(
        r"^client/maj_motdepasse/(?P<token>.+)/$",
        client_maj_mot_passe,
        name="client-motdepasse-maj",
    ),
    re_path(
        r"^prospect/inscrire/$",
        prospect_inscrire,
        name="prospect-inscrire",
    ),
    re_path(
        r"^monetico_s2s/$",
        monetico_s2s,
        name="monetico-s2s-old",
    ),
    re_path(
        r"^commande/monetico_s2s/$",
        monetico_s2s,
        name="monetico-s2s",
    ),
]

# Contenu

urlpatterns += [
    re_path(
        r"^actu/$",
        actu_liste,
        name="actu-liste",
    ),
    re_path(
        r"^actu/(?P<actu_url>.+)/$",
        actu_detail,
        name="actu-detail",
    ),
    re_path(
        r"^sitemap.xml$",
        sitemap,
        name="sitemap",
    ),
]

urlpatterns += [
    re_path(
        r"^distributeur-autocomplete/$",
        DistributeurAutocomplete.as_view(),
        name="distributeur-autocomplete",
    ),
    re_path(
        r"^typetarif-autocomplete/$",
        TarifFioulAutocomplete.as_view(),
        name="typetarif-autocomplete",
    ),
]


# Your other patterns here
urlpatterns += [
    re_path(
        r"^(?P<page_adresse>.+)/$",
        page_detail,
        name="page-detail",
    ),
]


# Debug toolbar
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
