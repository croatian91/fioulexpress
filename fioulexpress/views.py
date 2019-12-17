# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from django.template import RequestContext

import csv
import logging
import re
import weasyprint

from .forms import *
from .models import *
from monetico.iframe import get_iframe_src
from contenu.models import *
from decimal import Decimal
from django.template.loader import render_to_string, get_template
from django.utils._os import safe_join
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

logger = logging.getLogger(__name__)
# Create your views here.


class DistributeurAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_staff:
            return Distributeur.objects.none()

        qs = Distributeur.objects.all()

        if self.q:
            qs = qs.filter(nom__istartswith=self.q)

        return qs

class TarifFioulAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_staff:
            return TarifFioul.objects.none()

        qs = TarifFioul.objects.all()

        if self.q:
            qs = qs.filter(type_fioul__nom__istartswith=self.q)

        return qs

def home(request):
    if request.GET.get('msg', False):
        messages.add_message(request, messages.SUCCESS, "<p>Un exemple de validation OK !</p><p>Avec plusieurs petits paragraphes ...</p>")
        messages.add_message(request, messages.ERROR, "Un exemple de message d'erreur")
        messages.add_message(request, messages.SUCCESS, '''
            <p>Un message d\'info, avec un formulaire</p>
            <p>
                <form action="">
                    <input type="text" placeholder="email" />
                    <input type="submit" value="Valider" />
                </form>
            </p>
            ''')
    cp_inconnu = False
    if request.session.get('cp_inconnu', False):
        cp_inconnu = True
        del request.session['cp_inconnu']
    return render(request, 'home.html', {
        'actus' : Actualite.objects.order_by('-date')[:3],
        'cp_inconnu' : cp_inconnu,
        })

@staff_member_required
def distrib_hp(request):
    if request.user.is_superuser:
        if request.GET.get('distributeur', False):
            zones = Zone.objects.filter(distributeur=request.GET.get('distributeur')).exclude(archive=True)
        else:
            zones = []
    elif getattr(request.user, 'distributeur', False):
        zones = Zone.objects.filter(distributeur=request.user.distributeur).order_by('nom').exclude(archive=True)
    else:
        zones = []
    if request.user.is_superuser or request.user.groups.filter(name__in=('Comptable', 'Webmaster')).exists():
        return admin.sites.site.index(request)
    else:
        if not request.user.distributeur.zone_set.all():
            return redirect(reverse('distrib-zone-add'))
        return render(request, 'distrib/hp.html', {
            'has_permission' : True,
            'zones' : zones,
        })


@staff_member_required
def distrib_commandes(request):
    distributeur_form = DistribDalForm(request.GET)
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=('Comptable', 'Webmaster')).exists()
    if is_admin:
        if request.GET.get('distributeur', False):
            zones = Zone.objects.filter(distributeur=request.GET.get('distributeur')).exclude(archive=True)
            commandes = Commande.objects.filter(zone__distributeur=request.GET.get('distributeur'))
        else:
            commandes = Commande.objects.all()
            zones = []
    else:
        zones = Zone.objects.filter(distributeur=request.user.distributeur).order_by('nom').exclude(archive=True)
        commandes = Commande.objects.filter(zone__distributeur=request.user.distributeur)
    if request.GET.get('zone', False):
        zone_active = Zone.objects.get(id=request.GET.get('zone'))
        commandes = commandes.filter(zone=zone_active)
    else:
        zone_active = None
    if request.GET.get('statut', False):
        commandes = commandes.filter(statut=request.GET.get('statut'))
    if request.GET.get('client', False):
        commandes = commandes.filter(
            Q(adresse_livraison__nom__icontains=request.GET.get('client')) |
            Q(adresse_livraison__prenom__icontains=request.GET.get('client')) |
            Q(client__email__icontains=request.GET.get('client'))
        )
    if request.GET.get('du', False) or request.GET.get('au', False):
        recherche_form = DistribCommandeForm(request.GET)
        if recherche_form.is_valid():
            if request.GET.get('du', False):
                date_du = recherche_form.cleaned_data['du']
                commandes = commandes.filter(date__gt=recherche_form.cleaned_data['du'])
            if request.GET.get('au', False):
                date_au = recherche_form.cleaned_data['au']
                commandes = commandes.filter(date__lt=recherche_form.cleaned_data['au'])
    else:
        date_du = datetime.now() - timedelta(days=30)
        date_au = datetime.now() + timedelta(days=1)
        recherche_form = DistribCommandeForm(initial={
            'du' : date_du,
            'au' : date_au,
        })
        commandes = commandes.filter(date__gt=datetime.now() - timedelta(days=30))
    if request.GET.get('export', False):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="commandes-%s-%s.csv"' % (date_du.strftime('%d%m%Y'), date_au.strftime('%d%m%Y'))
        writer = csv.writer(response)
        writer.writerow([x.encode('utf-8') for x in [
            u'Distributeur', u'Zone', u'Statut',
            u'Commande ID', u'Référence Monetico', u"Numéro d'autorisation",
            u'Date', u'Date de livraison',
            u'Quantité', u'Type de fioul', u'Type de livraison',
            u'Commission TTC', u'Total TTC', u'Commission HT', u'Total HT',
            u'Livraison Nom', u'Livraison Prénom', u'Livraison adresse', u'Livraison code postal', u'Livraison ville',
            u'Facturation Nom', u'Facturation Prénom', u'Facturation adresse', u'Facturation code postal', u'Facturation ville',
        ]])
        for c in commandes:
            row = [
                c.zone.distributeur.nom, c.zone.nom, c.get_statut_display(),
                c.id, c.panier_id, c.monetico_id,
                c.date, c.date_livraison,
                c.qte, c.type_fioul.nom, c.type_livraison.nom,
                c.commission_ttc, c.total_ttc, c.commission_ht, c.total_ht,
                c.adresse_livraison.nom, c.adresse_livraison.prenom, c.adresse_livraison.detail_1, c.adresse_livraison.code_postal, c.adresse_livraison.detail_4,
            ]
            if c.adresse_facturation:
                row += [c.adresse_facturation.nom, c.adresse_facturation.prenom, c.adresse_facturation.detail_1, c.adresse_facturation.code_postal, c.adresse_facturation.detail_4]
            else:
                row += [c.adresse_livraison.nom, c.adresse_livraison.prenom, c.adresse_livraison.detail_1, c.adresse_livraison.code_postal, c.adresse_livraison.detail_4]
            writer.writerow([unicode(localize(x)).encode('utf-8') for x in row])
        return response
    return render(request, 'distrib/commandes.html', {
        'zones': zones,
        'zone_active' : zone_active,
        'commandes': commandes.order_by('-date'),
        'recherche_form' : recherche_form,
        'distributeur_form' : distributeur_form,
        'admin' : is_admin,
        'has_permission' : True,
    })

@staff_member_required
def distrib_commande_detail(request, id_commande):
    commande = Commande.objects.get(id=id_commande)
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=('Comptable', 'Webmaster')).exists()
    if not is_admin and commande.zone.distributeur != getattr(request.user, 'distributeur', False):
        return redirect(reverse('distrib-hp'))
    return render(request, 'distrib/commande_detail.html', {
        'admin' : is_admin,
        'commande' : commande,
        'has_permission' : True,
    })

@staff_member_required
def distrib_commande_annuler(request, id_commande):
    if request.user.is_superuser:
        c = Commande.objects.get(id=id_commande)
        c.statut = '1'
        c.save()
        return redirect(reverse('distrib-commandes'))


@staff_member_required
def distrib_produits(request):
    zones = Zone.objects.filter(distributeur=request.user.distributeur).order_by('nom').exclude(archive=True)
    config = Config.objects.filter(actif=True)[0]
    if request.GET.get('zone', False):
        zone_active = Zone.objects.get(id=request.GET.get('zone'))
    else:
        zone_active = zones[0]

    if request.POST:
        produits_formset = DistribTarifFioulForm(request.POST, instance=zone_active)
        decotes_formset = DistribTarifDecoteForm(request.POST, instance=zone_active)
        livraisons_formset = DistribTarifLivraisonForm(request.POST, instance=zone_active)
        if produits_formset.is_valid() and decotes_formset.is_valid() and livraisons_formset.is_valid():
            produits_formset.save()
            decotes_formset.save()
            livraisons_formset.save()
            messages.add_message(request, messages.SUCCESS, 'La zone a été modifiée avec succès')
            return redirect(reverse('distrib-produits') + '?zone=%s' % zone_active.id)
        else:
            messages.add_message(request, messages.ERROR, "La zone n'a pas été modifiée")
    else:
        produits_formset = DistribTarifFioulForm(instance=zone_active)
        decotes_formset = DistribTarifDecoteForm(instance=zone_active)
        livraisons_formset = DistribTarifLivraisonForm(instance=zone_active)

    livraisons = []
    for tarif_id in (3, 2, 1):
        t = TarifLivraison.objects.get(zone=zone_active, type_livraison=tarif_id)
        if t.actif:
            livraisons.append(t)
    tarifs = []
    for tarif_fioul in zone_active.tariffioul_set.filter(actif=True).order_by('type_fioul__position'):
        tarif = {'nom':tarif_fioul.type_fioul.nom, 'decotes':[]}
        for decote in zone_active.tarifdecote_set.order_by('min'):
            tarifs_decote_livraison = {
                'jaune' : decote.min == 1000,
                'ligne' : ['%s - %s' % (decote.min, decote.max)]
            }
            for livraison in livraisons:
                tarifs_decote_livraison['ligne'].append(round(tarif_fioul.prix_ttc + decote.decote + livraison.extra, 4))
            tarif['decotes'].append(tarifs_decote_livraison)
        tarifs.append(tarif)
    return render(request, 'distrib/produits.html', {
        'zones': zones,
        'zone_active' : zone_active,
        'produits_formset' : produits_formset,
        'decotes_formset' : decotes_formset,
        'livraisons_formset' : livraisons_formset,
        'tarifs' : tarifs,
        'livraisons' : livraisons,
        'commission' :-1 * config.commission,
        'has_permission' : True,
    })

@staff_member_required
def distrib_livraisons(request):
    distributeur_form = DistribDalForm(request.GET)
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=('Comptable', 'Webmaster')).exists()
    if request.user.is_superuser:
        if request.GET.get('distributeur', False):
            zones = Zone.objects.filter(distributeur=request.GET.get('distributeur')).exclude(archive=True)
            commandes = Commande.objects.filter(zone__distributeur=request.GET.get('distributeur'))
        else:
            commandes = Commande.objects.all()
            zones = []
    else:
        zones = Zone.objects.filter(distributeur=request.user.distributeur).order_by('nom').exclude(archive=True)
        commandes = Commande.objects.filter(zone__distributeur=request.user.distributeur)
    if request.GET.get('zone', False):
        zone_active = Zone.objects.get(id=request.GET.get('zone'))
        commandes = commandes.filter(zone=zone_active)
    else:
        zone_active = None

    code_postaux = []
    zone_form = False
    if zone_active:
        if request.POST:
            # livraisons_formset = DistribTarifLivraisonForm(request.POST, instance=zone_active)
            zone_form = ZoneForm(request.POST, instance=zone_active)
            # if livraisons_formset.is_valid() and zone_form.is_valid():
            if zone_form.is_valid():
                # livraisons_formset.save()
                zone_form.save()
                messages.add_message(request, messages.SUCCESS, 'La zone a été modifiée avec succès')
                # return redirect('/distrib/livraisons/?zone=%s' % zone_active.id)
                return redirect(reverse('distrib-livraisons') + '?zone=%s' % zone_active.id)
            else:
                messages.add_message(request, messages.ERROR, "La zone n'a pas été modifiée")
        else:
            # livraisons_formset = DistribTarifLivraisonForm(instance=zone_active)
            zone_form = ZoneForm(instance=zone_active)

        code_postaux = zone_active.codepostal_set.order_by('code_postal').values_list('code_postal', flat=True).distinct()

        code_postaux = []
        departement_code = ''
        departement = {}
        for cp in zone_active.codepostal_set.order_by('code_postal').values_list('code_postal', flat=True).distinct():
            if departement_code != cp[:2]:
                if departement:
                    code_postaux.append(departement)
                departement_code = cp[:2]
                departement = {'departement' : departement_code, 'code_postaux':[]}
            departement['code_postaux'].append(cp)
        if departement:
            code_postaux.append(departement)

    return render(request, 'distrib/livraisons.html', {
        'zones': zones,
        'zone_active' : zone_active,
        'distributeur_form' : distributeur_form,
        # 'livraisons_formset' : livraisons_formset,
        'livraisons' : zone_active and zone_active.tariflivraison_set.order_by('type_livraison__position') or [],
        'code_postaux' : code_postaux,
        'zone_form' : zone_form,
        'nb_communes' : zone_active and zone_active.codepostal_set.count() or None,
        'est_admin' : request.user.is_superuser or not request.user.distributeur.actif or (zone_active and not zone_active.actif),
        'admin' : is_admin,
        'has_permission' : True,
    })

@staff_member_required
def distrib_remove_cp(request, cp):
    if request.user.is_superuser:
        zones = Zone.objects.all()
    else:
        zones = Zone.objects.filter(distributeur=request.user.distributeur).order_by('nom')
    if request.GET.get('zone', False):
        zone_active = zones.get(id=request.GET.get('zone'))
    else:
        zone_active = None
    if zone_active:
        msg = False
        if len(cp) < 5:
            cp_liste = CodePostal.objects.filter(code_postal__startswith=cp)
        else:
            cp_liste = CodePostal.objects.filter(code_postal=cp)
        for c in cp_liste:
            if zone_active == c.zone:
                c.zone = None
                c.save()
                if not msg:
                    msg = True
                    messages.add_message(request, messages.SUCCESS, u"Le code postal %s a été enlevé" % cp)
    return redirect(reverse('distrib-livraisons') + '?zone=' + str(zone_active.id))

@staff_member_required
def distrib_import_cp(request):
    if request.user.is_superuser:
        zones = Zone.objects.all()
    else:
        zones = Zone.objects.filter(distributeur=request.user.distributeur).order_by('nom')
    if request.GET.get('zone', False):
        zone_active = zones.get(id=request.GET.get('zone'))
    else:
        zone_active = None

    if zone_active:
        if request.POST.get('cp_liste', False):
            liste_cp = re.sub('[^\d]+', ',', request.POST.get('cp_liste'))
            non_importe = []
            nb_importes = 0
            for cp_search in liste_cp.split(','):
                if len(cp_search) > 1:
                    for cp in CodePostal.objects.filter(code_postal__startswith=cp_search).order_by('code_postal').values_list('code_postal', flat=True).distinct():
                        communes = CodePostal.objects.filter(code_postal=cp)
                        if communes.filter(zone__isnull=True):
                            for c in communes:
                                c.zone = zone_active
                                c.save()
                            nb_importes += 1
                        else:
                            if len(cp) > 0:
                                non_importe.append(cp)
            if nb_importes > 0:
                messages.add_message(request, messages.SUCCESS, u"Nombre de codes postaux importés : %s" % nb_importes)
            if len(non_importe) > 1:
                messages.add_message(request, messages.WARNING, u"Les codes postaux %s sont déjà attribués à l'un de nos distributeurs. Pour toute question, veuillez contactez admin@fioulexpres.fr" % ','.join(non_importe))
            if len(non_importe) == 1:
                messages.add_message(request, messages.WARNING, u"Le code postal %s est déjà attribué à l'un de nos distributeurs. Pour toute question, veuillez contactez admin@fioulexpres.fr" % non_importe[0])
    return redirect(reverse('distrib-livraisons') + '?zone=' + str(zone_active.id))

@staff_member_required
def distrib_inscription(request):
    erreurs = {}
    if request.POST:
        if request.POST.get('username'):
            username = request.POST.get('username')
            if not User.objects.filter(username=username):
                if request.POST.get('password') and request.POST.get('password_confirm'):
                    password = request.POST.get('password')
                    password_confirm = request.POST.get('password_confirm')
                    if password != password_confirm:
                        erreurs['text'] = "Le mot de passe est différent de sa confirmation"
                    elif len(password) < 8:
                        erreurs['text'] = "Le mot de passe doit faire au moins 8 caractères"
                else:
                    erreurs['text'] = "Vous devez renseigner un mot de passe et le confirmer"
            else:
                erreurs['text'] = "Cet identifiant est déjà utilisé"
        else:
            erreurs['text'] = "Vous devez renseigner un identifiant"
        if not erreurs:
            distrib = Distributeur.objects.create(nom=username, actif=False)
            distrib.user = User.objects.create(username=distrib.nom)
            distrib.user.set_password(password)
            distrib.user.is_staff = True
            distrib.user.groups.add(1)
            distrib.user.save()
            distrib.save()
            user_actif = authenticate(username=username, password=password)
            login(request, user_actif)
            return redirect('/distributeur/')
    return render(request, 'distrib/inscription.html', {
        'erreurs':erreurs,
    })

@staff_member_required
def distrib_zone_add(request):
    if request.POST:
        zone_form = DistribZoneForm(request.POST)
        if zone_form.is_valid():
            zone = zone_form.save()
            zone.distributeur = request.user.distributeur
            zone.save()
            for type_fioul in TypeFioul.objects.all():
                TarifFioul.objects.create(type_fioul=type_fioul, prix_ttc=10000, zone=zone, actif=False)
            for type_livraison in TypeLivraison.objects.all():
                TarifLivraison.objects.create(type_livraison=type_livraison, extra=0, zone=zone, actif=False)
            TarifDecote.objects.create(min=500, max=999, zone=zone, decote=0)
            TarifDecote.objects.create(min=1000, max=1999, zone=zone, decote=0)
            TarifDecote.objects.create(min=2000, max=2999, zone=zone, decote=0)
            TarifDecote.objects.create(min=3000, max=3999, zone=zone, decote=0)
            TarifDecote.objects.create(min=4000, max=4999, zone=zone, decote=0)
            # TarifDecote.objects.create(min=5000, max=5999, zone=zone, decote=0)
            TarifDecote.objects.create(min=5000, max=10000, zone=zone, decote=0)
            return redirect(reverse('distrib-livraisons') + '?zone=' + str(zone.id))
    else:
        zone_form = DistribZoneForm()
    return render(request, 'distrib/zone.html', {
        'zone_form' : zone_form,
        'has_permission' : True,
    })


def admin_se_connecter_distrib(request, id_distributeur):
    if request.user.is_superuser:
        d = Distributeur.objects.get(id=id_distributeur)
        d.user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, d.user)
    return redirect('/distributeur/')

def client_valide_cp(request):
    try:
        code_postal = CodePostal.objects.filter(code_postal=request.POST['cp'])[0]
    except:
        request.session['cp_inconnu'] = True
        logger.error("CP inconnu: {}".format(request.POST['cp']))
        # messages.add_message(request, messages.ERROR, "Désolé, ce code postal est inconnu")
        return redirect('/')
    if not code_postal.zone or code_postal.zone.archive or not code_postal.zone.actif or not code_postal.zone.distributeur.actif:
        msg = render_to_string('commande/prospect_inscription_form.html', RequestContext(request))
        messages.add_message(request, messages.INFO, msg)
        return redirect('/')
    request.session['client_cp'] = request.POST['cp']
    request.session['client_zone'] = code_postal.zone.id
    return redirect('/commande/devis/')

def prospect_inscrire(request):
    if request.POST.get('email', False):
        Prospect.objects.create(email=request.POST.get('email'), code_postal=request.POST.get('cp'))
        messages.add_message(request, messages.SUCCESS, "Votre email a été enregistré")
    return redirect('/')

def client_commande_devis(request):
    try:
        zone_active = Zone.objects.get(id=request.session['client_zone'])
    except:
        return redirect('/')
    return render(request, 'commande/devis.html', {
        'zone_active' : zone_active,
    })

def client_commande_valoriser(request):
    data = json.loads(request.body)
    if request.session.get('panier_id', False):
        panier = Panier.objects.get(id=request.session['panier_id'])
    else:
        panier = Panier()
    panier.zone_id = data['zone']
    panier.type_fioul_id = data['type_fioul']
    panier.type_livraison_id = data['type_livraison']
    panier.qte = Decimal(data['qte'])
    panier.save()
    request.session['panier_id'] = panier.id
    request.session['panier_valeur'] = panier.valeur()

    livraison_prix = request.session['panier_valeur']['livraison_ttc']
    if livraison_prix >= 0:
        request.session['panier_valeur']['livraison_prix'] = u'+ %s€' % localize(floatformat(livraison_prix, 2))
    else:
        request.session['panier_valeur']['livraison_prix'] = u'- %s€' % localize(floatformat(livraison_prix * -1, 2))

    request.session['panier_valeur']['prix_litre'] = localize(floatformat(request.session['panier_valeur']['prix_litre'], '-3'))
    request.session['panier_valeur']['total_ttc'] = localize(floatformat(request.session['panier_valeur']['total_ttc'], '-2'))
    request.session['panier_valeur']['total_ht'] = localize(floatformat(request.session['panier_valeur']['total_ht'], '-2'))

    for k in ['livraison_ttc', 'acompte', 'acompte_ht', 'reste']:
        request.session['panier_valeur'][k] = localize(floatformat(request.session['panier_valeur'][k], -2))

    return HttpResponse(json.dumps(request.session['panier_valeur']))

def client_commande_livraison(request):
    if request.user and request.user.is_staff:
        messages.error(request, "Vous etes connecté en tant que membre de l'équipe, <a href=\"/distributeur/logout/?next=/\">se deconnecter</a>")
        return redirect('/')
    try:
        zone_active = Zone.objects.get(id=request.session['client_zone'])
        panier = Panier.objects.get(id=request.session['panier_id'])
    except:
        return redirect('/')
    if getattr(request.user, 'client', False):
        panier.set_client(request.user.client)
    if request.POST:
        client_form = ClientForm(request.POST, prefix='client', instance=panier.client)
        adresse_livraison_form = AdresseForm(request.POST, prefix='adresse-livraison', instance=panier.adresse_livraison)
        adresse_livraison_form['detail_4'].field.choices = CodePostal.objects.filter(code_postal=request.session['client_cp']).values_list('commune', 'commune')
        adresse_facturation_form = AdresseFacturationForm(request.POST, prefix='adresse-facturation', instance=panier.adresse_facturation)
        commentaire_form = PanierForm(request.POST, prefix='commentaire', instance=panier)
        panier = commentaire_form.save()
        if client_form.is_valid():
            if adresse_livraison_form.is_valid():
                client = client_form.save()
                client.email = client.email.lower()
                client.save()
                adresse_livraison_form.instance.client = client
                adresse_livraison = adresse_livraison_form.save()
                adresse_livraison.code_postal = request.session['client_cp']
                adresse_livraison.save()
                panier.client = client
                panier.adresse_livraison = adresse_livraison
                if request.POST.get('creer_compte', False):
                    if request.POST.get('creer_compte_password', False):
                        if Client.objects.filter(email=client.email, user__isnull=False):
                            messages.add_message(request, messages.ERROR, "Un compte existe déjà avec cet email, <a href=\"/client/connexion/?next=/commande/livraison/\">connectez-vous</a>")
                            return render(request, 'commande/livraison.html', {
                                'zone_active' : zone_active,
                                'panier' : panier,
                                'client_form' : client_form,
                                'erreur_password' : True,
                                'adresse_livraison_form' : adresse_livraison_form,
                                'adresse_facturation_form' : adresse_facturation_form,
                            })
                        else:
                            user = User()
                            user.username = client.email[:30]
                            user.set_password(request.POST.get('creer_compte_password'))
                            user.save()
                            client.user = user
                            client.save()
                            user_actif = authenticate(username=user.username, password=request.POST.get('creer_compte_password'))
                            login(request, user_actif)
                    else:
                        return render(request, 'commande/livraison.html', {
                            'zone_active' : zone_active,
                            'panier' : panier,
                            'client_form' : client_form,
                            'erreur_password' : True,
                            'adresse_livraison_form' : adresse_livraison_form,
                            'adresse_facturation_form' : adresse_facturation_form,
                        })

                if request.POST.get('facturation_differente', False):
                    adresse_facturation_form.instance.client = client
                    if adresse_facturation_form.is_valid():
                        adresse_facturation = adresse_facturation_form.save()
                        adresse_facturation.nom_adresse = 'facturation'
                        adresse_facturation.save()
                        panier.adresse_facturation = adresse_facturation
                        panier.save()
                        return redirect(reverse('client-commande-paiement'))
                else:
                    # panier.adresse_facturation = adresse_livraison
                    panier.adresse_facturation = None
                    panier.save()
                    return redirect(reverse('client-commande-paiement'))

    else:
        client_form = ClientForm(prefix='client', instance=panier.client)
        adresse_livraison_form = AdresseForm(prefix='adresse-livraison', instance=panier.adresse_livraison)
        adresse_livraison_form['detail_4'].field.choices = CodePostal.objects.filter(code_postal=request.session['client_cp']).order_by('commune').values_list('commune', 'commune')
        instance_panier_adresse_facturation = None
        if panier.adresse_facturation:
            instance_panier_adresse_facturation = panier.adresse_facturation
        elif panier.client:
            factu = panier.client.adresse_set.filter(nom_adresse='facturation')
            if factu:
                instance_panier_adresse_facturation = factu[0]
        adresse_facturation_form = AdresseFacturationForm(prefix='adresse-facturation', instance=instance_panier_adresse_facturation)
        commentaire_form = PanierForm(prefix='commentaire', instance=panier)
    return render(request, 'commande/livraison.html', {
        'zone_active' : zone_active,
        'panier' : panier,
        'client_form' : client_form,
        'adresse_livraison_form' : adresse_livraison_form,
        'adresse_facturation_form' : adresse_facturation_form,
        'commentaire_form' : commentaire_form,
    })

def client_commande_paiement(request):
    try:
        zone_active = Zone.objects.get(id=request.session['client_zone'])
        panier = Panier.objects.get(id=request.session['panier_id'])
    except:
        return redirect('/')
    return render(request, 'commande/paiement.html', {
        'zone_active' : zone_active,
        'panier' : panier,
        'panier_valeur' : panier.valeur(),
        'iframe_url' : get_iframe_src(panier, request),
    })

def client_commande_monetico_ok(request):
    try:
        zone_active = Zone.objects.get(id=request.session['client_zone'])
        panier = Panier.objects.get(id=request.session['panier_id'])
    except:
        messages.add_message(request, messages.ERROR, "Le paiement n'a pas pu être validé")
    # c = panier.creer_commande()
    # request.session['commande_id'] = c.id
    # del request.session['panier_id']
    # del request.session['client_zone']
    # panier.delete()
    return redirect(reverse('client-commande-confirmation'))

def client_commande_monetico_ko(request):
    messages.add_message(request, messages.ERROR, "Le paiement n'a pas pu être validé")
    return redirect('/commande/paiement/')

def client_commande_confirmation(request):
    try:
        zone_active = Zone.objects.get(id=request.session['client_zone'])
        panier = Panier.objects.get(id=request.session['panier_id'])
    except:
        return redirect('/')
    # try:
    #    commande = Commande.objects.get(id=request.session['commande_id'])
    # except:
    #    return redirect('/')
    return render(request, 'commande/confirmation.html', {
        'panier' : panier,
        'panier_valeur' : panier.valeur(),
    })

@csrf_exempt
def monetico_s2s(request):
    # sleep(10)
    # yield uwsgi.async_sleep(2)
    if request.POST.get('code-retour', '') not in ('payetest', 'paiement'):
        return HttpResponse('version=2\ncdr=0\n')
    panier = Panier.objects.get(id=request.POST.get('reference', ''))
    c = panier.creer_commande()
    # c = Commande.objects.get(panier_id=request.POST.get('reference', ''))
    c.monetico_id = request.POST.get('numauto', '')
    c.statut = '0'
    c.save()
    email_data = json.dumps(c.data())
    # mail client
    Message.objects.create(
        type_id=2,
        user=c.client.user,
        sujet='Fioul Express - Confirmation de commande',
        destinataire=c.client.email,
        data=email_data,
    )
    # mail distributeur
    Message.objects.create(
        type_id=3,
        user=c.zone.distributeur.user,
        sujet='Fioul Express - Confirmation de commande #%s' % c.id,
        destinataire=c.zone.email,
        data=email_data,
    )
    # mail admin
    Message.objects.create(
        type_id=4,
        sujet='Fioul Express - Confirmation de commande #%s' % c.id,
        destinataire=Config.objects.filter(actif=True)[0].email_admin,
        data=email_data,
    )
    return HttpResponse('version=2\ncdr=0\n')




def client_connexion(request):
    if request.POST:
        try:
            client = Client.objects.get(email=request.POST.get('email'), user__isnull=False)
            user_actif = authenticate(username=client.user.username, password=request.POST.get('password'))
            login(request, user_actif)
            if request.session.get('panier_id', False):
                panier = Panier.objects.get(id=request.session['panier_id'])
                panier.set_client(client)
            request.session['client_zone'] = panier.zone.id
            request.session['panier_id'] = panier.id
            return redirect(request.GET.get('next', '/'))
        except:
            messages.add_message(request, messages.ERROR, "Les informations fournies n'ont pas permis de vous identifier")
    return render(request, 'client/connexion.html', {
    })

def client_deconnexion(request):
    logout(request)
    messages.add_message(request, messages.INFO, "Vous avez été deconnecté")
    return redirect(request.GET.get('next', '/'))

def client_recuperation_mot_passe(request):
    messages.add_message(request, messages.INFO, "Si votre email correspond à un compte client, vous recevrez dans quelques minutes un email permettant de modifier votre mot de passe.")
    if request.POST.get('email', False):
        email = request.POST.get('email').lower()
        for client in Client.objects.filter(user__isnull=False, email=email):
            token = client.set_token()
            data = {
                'lien_password' : 'https://' + request.META['HTTP_HOST'] + reverse('client-motdepasse-maj', args=[token])
            }
            msg = Message.objects.create(
                type_id=1,
                user=client.user,
                sujet='Modification du mot de passe',
                destinataire=client.email,
                data=json.dumps(data),
            )
            return redirect('/')
    return redirect('/')

def client_maj_mot_passe(request, token=''):
    try:
        client = Client.objects.get(token_password=token, token_date__gte=datetime.now())
    except:
        messages.add_message(request, messages.ERROR, 'Le lien a expiré')
        return redirect('/')
    if request.POST.get('password', False):
        client.user.set_password(request.POST['password'])
        client.user.save()
        client.token_password = ''
        client.token_date = datetime.now() - timedelta(days=2)
        client.save()
        messages.add_message(request, messages.SUCCESS, 'Le mot de passe a été mis à jour')
        return redirect('/')
    return render(request, 'client/maj_mot_de_passe.html', {
        'client' : client,
    })

def url_fetcher(url):
    if url.startswith('assets://'):
        url = url[len('assets://'):]
        url = "file://" + safe_join(settings.ASSETS_ROOT, url)
    return weasyprint.default_url_fetcher(url)

def admin_commande_pdf(request, commande_id):
    if not request.user.is_staff:
        return redirect('/')
    commande = Commande.objects.get(id=commande_id)
    if getattr(request.user, 'distributeur', False) and request.user.distributeur != commande.zone.distributeur:
        return redirect('/')
    template = get_template("admin/commande/detail_pdf.html")
    context = {'commande' : commande}
    html = template.render(RequestContext(request, context))
    response = HttpResponse(content_type="application/pdf")
    weasyprint.HTML(string=html, url_fetcher=url_fetcher).write_pdf(response)
    return response
