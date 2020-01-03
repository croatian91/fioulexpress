"""fioul URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from fioulexpress.views import *
from contenu.views import *


urlpatterns = [
    url(r'^$', home),
    url(r'^markdownx/', include('markdownx.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^admin/', admin.site.urls),
]

# Interface distributeur
urlpatterns += [
    url(
        r'^distributeur/commande/$',
        distrib_commandes,
        name='distrib-commandes',
    ),
    url(
        r'^distributeur/commande/(?P<id_commande>\d+)/annuler/$',
        distrib_commande_annuler,
        name='distrib-commande-annuler',
    ),
    url(
        r'^distributeur/commande/(?P<commande_id>\d+)/pdf/$',
        admin_commande_pdf,
        name='distrib-commande-pdf',
    ),
    url(
        r'^distributeur/commande/(?P<id_commande>\d+)/$',
        distrib_commande_detail,
        name='distrib-commande-detail',
    ),
    # url(
    #    r'^distributeur/inscription/$',
    #    distrib_inscription,
    #    name='distrib-inscription',
    # ),
    url(
        r'^distributeur/produits/$',
        distrib_produits,
        name='distrib-produits',
    ),
    url(
        r'^distributeur/livraisons/$',
        distrib_livraisons,
        name='distrib-livraisons',
    ),
    url(
        r'^distributeur/creer_zone/$',
        distrib_zone_add,
        name='distrib-zone-add',
    ),
    url(
        r'^distributeur/remove_cp/(?P<cp>.+)/$',
        distrib_remove_cp,
        name='distrib-remove-cp',
    ),
    url(
        r'^distributeur/import_cp/$',
        distrib_import_cp,
        name='distrib-import-cp',
    ),
    url(
        r'^distributeur/se_connecter_distrib/(?P<id_distributeur>\d+)/$',
        admin_se_connecter_distrib,
        name='se-connecter-distrib',
    ),
    url(
        r'^distributeur/$',
        distrib_hp,
        name='distrib-hp',
    ),
    url(r'^distributeur/', admin.site.urls),
]

# Interface client
urlpatterns += [
    url(
        r'^commande/valide_cp/$',
        client_valide_cp,
        name='client-valide-cp',
    ),
    url(
        r'^commande/devis/$',
        client_commande_devis,
        name='client-commande-devis',
    ),
    url(
        r'^commande/valoriser/$',
        client_commande_valoriser,
        name='client-commande-valoriser',
    ),
    url(
        r'^commande/livraison/$',
        client_commande_livraison,
        name='client-commande-livraison',
    ),
    url(
        r'^commande/paiement/$',
        client_commande_paiement,
        name='client-commande-paiement',
    ),
    url(
        r'^commande/confirmation/$',
        client_commande_confirmation,
        name='client-commande-confirmation',
    ),
    url(
        r'^commande/monetico_ok/$',
        client_commande_monetico_ok,
        name='client-commande-monetico-ok',
    ),
    url(
        r'^commande/monetico_ko/$',
        client_commande_monetico_ko,
        name='client-commande-monetico-ko',
    ),
    url(
        r'^client/connexion/$',
        client_connexion,
        name='client-connexion',
    ),
    url(
        r'^client/deconnexion/$',
        client_deconnexion,
        name='client-deconnexion',
    ),
    url(
        r'^client/motdepasse/$',
        client_recuperation_mot_passe,
        name='client-motdepasse',
    ),
    url(
        r'^client/maj_motdepasse/(?P<token>.+)/$',
        client_maj_mot_passe,
        name='client-motdepasse-maj',
    ),
    url(
        r'^prospect/inscrire/$',
        prospect_inscrire,
        name='prospect-inscrire',
    ),
    url(
        r'^monetico_s2s/$',
        monetico_s2s,
        name='monetico-s2s-old',
    ),
    url(
        r'^commande/monetico_s2s/$',
        monetico_s2s,
        name='monetico-s2s',
    ),
]

# Contenu

urlpatterns += [
    url(
        r'^actu/$',
        actu_liste,
        name='actu-liste',
    ),
    url(
        r'^actu/(?P<actu_url>.+)/$',
        actu_detail,
        name='actu-detail',
    ),
    url(
        r'^sitemap.xml$',
        sitemap,
        name='sitemap',
    ),
]

urlpatterns += [
    url(
        r'^distributeur-autocomplete/$',
        DistributeurAutocomplete.as_view(),
        name='distributeur-autocomplete',
    ),
    url(
        r'^typetarif-autocomplete/$',
        TarifFioulAutocomplete.as_view(),
        name='typetarif-autocomplete',
    ),
]


# Your other patterns here
urlpatterns += [
    url(
        r'^(?P<page_adresse>.+)/$',
        page_detail,
        name='page-detail',
    ),
]


# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
