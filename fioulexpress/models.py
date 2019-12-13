# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.templatetags.l10n import localize
from django.template.defaultfilters import floatformat
from multiselectfield import MultiSelectField
from decimal import Decimal
from datetime import datetime, timedelta
from django.template.defaultfilters import date as template_date
from django.core.urlresolvers import reverse


class CodePostal(models.Model):
    code_postal = models.CharField(max_length=5)
    commune = models.CharField(max_length=255, null=True)
    zone = models.ForeignKey('Zone', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Codes Postaux'

    def __unicode__(self):
        return '%s (%s)' % (self.code_postal, self.commune)

class Config(models.Model):
    nom = models.CharField(max_length=100, default='Standard')
    commission = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    heure_limite_livraison = models.IntegerField(default=19)
    actif = models.BooleanField(default=False)
    taux_tva = models.DecimalField(max_digits=10, decimal_places=4, default=0.2)
    email_admin = models.EmailField()
    google_analytics_ua = models.CharField(max_length=25, null=True, blank=True)
    meta_description = models.CharField(max_length=500, null=True, blank=True)
    meta_title = models.CharField(max_length=500, null=True, blank=True)
    meta_img = models.ImageField(null=True, blank=True)

    def __unicode__(self):
        return self.nom


class Distributeur(models.Model):
    nom = models.CharField(max_length=255)
    user = models.OneToOneField(User, null=True)
    informations = models.TextField(blank=True)
    actif = models.BooleanField(default=False)

    def __unicode__(self):
        return self.nom

    def admin_se_connecter_distributeur(self):
        return '<a href="%s" target="_blank">Se connecter</a>' % reverse('se-connecter-distrib', kwargs={'id_distributeur':self.id})
    admin_se_connecter_distributeur.allow_tags = True
    admin_se_connecter_distributeur.short_description = ' '

class JourFerie(models.Model):
    date = models.DateField()

    def __unicode__(self):
        return self.date.isoformat()

class TarifDecote(models.Model):
    zone = models.ForeignKey('Zone')
    min = models.IntegerField(default=500)
    max = models.IntegerField(default=1000)
    decote = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    def __unicode__(self):
        return str(self.id)

class TarifFioul(models.Model):
    type_fioul = models.ForeignKey('TypeFioul')
    zone = models.ForeignKey('Zone')
    prix_ttc = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['type_fioul__position']

    def __unicode__(self):
        return str(self.id)




class TarifLivraison(models.Model):
    type_livraison = models.ForeignKey('TypeLivraison')
    zone = models.ForeignKey('Zone')
    extra = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    actif = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.id)


    def candidat_valide(self, candidat):
        jours_feries = JourFerie.objects.filter(date__gte=datetime.now()).values_list('date', flat=True)
        if str(candidat.weekday()) in self.zone.jours_livraison:
            if not datetime.date(candidat) in jours_feries:
                return True
        return False

    def date_livraison(self):
        config_fioul = Config.objects.filter(actif=True)[0]
        candidat = datetime.today()
        reste = self.type_livraison.duree
        if candidat.hour >= config_fioul.heure_limite_livraison or not self.candidat_valide(candidat):
            reste += 1
        index = 0
        while reste > 0 and index < 30:
            candidat += timedelta(days=1)
            index += 1
            if self.candidat_valide(candidat):
                reste -= 1
        return candidat


class TypeFioul(models.Model):
    nom = models.CharField(max_length=255)
    position = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'type de fioul'
        verbose_name_plural = 'types de fiouls'
        ordering = ['position']

    def __unicode__(self):
        return self.nom

class TypeLivraison(models.Model):
    nom = models.CharField(max_length=255)
    duree = models.IntegerField(default=1)
    position = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'type de livraison'
        verbose_name_plural = 'types de livraisons'
        ordering = ['position']

    def __unicode__(self):
        return self.nom

    def temps_livraison(self):
        if self.duree > 1:
            return '%s jours' % self.duree
        else:
            return '24h'


JOURS_SEMAINE = (('0', 'lundi'),
                ('1', 'mardi'),
                ('2', 'mercredi'),
                ('3', 'jeudi'),
                ('4', 'vendredi'),
                ('5', 'samedi'),
                ('6', 'dimanche'),)
TYPES_PAIEMENT = (('0', 'chèque'),
                ('1', 'espèces'),
                ('2', 'CB'),)

class Zone(models.Model):
    distributeur = models.ForeignKey('Distributeur', null=True)
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=255, null=True)
    raison_sociale = models.CharField(max_length=255, null=True)
    siret = models.CharField(max_length=14, null=True)
    adresse = models.CharField(max_length=255, null=True)
    code_postal = models.CharField(max_length=5, null=True)
    ville = models.CharField(max_length=255, null=True)
    jours_livraison = MultiSelectField(choices=JOURS_SEMAINE, null=True, blank=True)
    types_paiement = MultiSelectField(choices=TYPES_PAIEMENT, null=True, blank=True)
    actif = models.BooleanField(default=True)
    archive = models.BooleanField(default=False)


    def __unicode__(self):
        return '%s - %s' % (self.distributeur.nom, self.nom)

    def paiements_acceptes(self):
        paiements = []
        for i in TYPES_PAIEMENT:
            if i[0] in self.types_paiement:
                paiements.append(i[1])
        if len(paiements) == 3:
            return '%s, %s ou %s' % tuple(paiements)
        if len(paiements) == 2:
            return '%s ou %s' % tuple(paiements)
        if len(paiements) == 1:
            return '%s' % tuple(paiements)
        return 'à confirmer avec le distributeur'

    def fiouls(self):
        return self.tariffioul_set.filter(actif=True).order_by('type_fioul__position')

    def livraisons(self):
        return self.tariflivraison_set.filter(actif=True).order_by('type_livraison__position')

    def delete(self):
        return False



# client

class Adresse(models.Model):
    client = models.ForeignKey('Client', null=True, blank=True)
    nom_adresse = models.CharField(max_length=255, default='adresse_par_defaut')
    prenom = models.CharField(max_length=255)
    nom = models.CharField(max_length=255)
    societe = models.CharField(max_length=255, null=True, blank=True)
    detail_1 = models.CharField('Adresse', max_length=255)
    detail_4 = models.CharField('Ville', max_length=255, null=True, blank=True)
    code_postal = models.CharField('Code postal', max_length=10)
    pays = models.CharField(max_length=50, default='France')

    def __unicode__(self):
        return '%s - %s' % (self.client, self.nom_adresse)

class Client(models.Model):
    user = models.OneToOneField(User, null=True)
    email = models.EmailField()
    telephone = models.CharField(max_length=25)
    token_password = models.CharField(max_length=100, null=True, blank=True)
    token_date = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return self.email

    def set_token(self):
        self.token_password = uuid.uuid4()
        self.token_date = datetime.now() + timedelta(days=4)
        self.save()
        return self.token_password

class Panier(models.Model):
    zone = models.ForeignKey('Zone')
    client = models.ForeignKey('Client', null=True, blank=True)
    adresse_livraison = models.ForeignKey('Adresse', related_name='+', null=True, blank=True)
    adresse_facturation = models.ForeignKey('Adresse', related_name='+', null=True, blank=True)
    type_fioul = models.ForeignKey('TypeFioul', null=True, blank=True)
    type_livraison = models.ForeignKey('TypeLivraison', null=True, blank=True)
    qte = models.IntegerField(default=1000)
    commentaire = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.zone.nom

    def valeur(self):
        retour = {}
        tarif = TarifFioul.objects.get(zone=self.zone, type_fioul=self.type_fioul)
        decote = TarifDecote.objects.get(zone=self.zone, min__lte=self.qte, max__gte=self.qte)
        livraison = TarifLivraison.objects.get(zone=self.zone, type_livraison=self.type_livraison)
        config = Config.objects.filter(actif=True)[0]
        retour['total_ttc'] = (tarif.prix_ttc + decote.decote + livraison.extra) * Decimal(self.qte) / Decimal(1000)
        retour['prix_litre'] = retour['total_ttc'] / Decimal(self.qte)
        # retour['total_ttc'] += livraison.extra
        retour['total_ht'] = retour['total_ttc'] / (Decimal('1') + config.taux_tva)
        retour['livraison_ttc'] = livraison.extra
        retour['livraison_nom'] = livraison.type_livraison.nom
        retour['livraison_date'] = template_date(livraison.date_livraison(), 'l j F')
        retour['livraisons'] = {}
        liv_prix_base = livraison.extra * Decimal(self.qte) / Decimal(1000)
        for liv in TarifLivraison.objects.filter(zone=self.zone, actif=True):
            liv_label = ''
            if self.type_livraison != liv.type_livraison:
                liv_prix = (liv.extra * Decimal(self.qte) / Decimal(1000)) - liv_prix_base
                if liv_prix > 0:
                    liv_label = '+ ' + localize(floatformat(liv_prix, '-2')) + ' euros'
                elif liv_prix < 0:
                    liv_label = '- ' + localize(floatformat(-1 * liv_prix, '-2')) + ' euros'
            retour['livraisons'][liv.id] = liv_label
        retour['fioul_nom'] = tarif.type_fioul.nom
        retour['qte'] = int(self.qte)

        retour['acompte'] = config.commission * self.qte / 1000
        retour['acompte_ht'] = retour['acompte'] / (1 + config.taux_tva)
        retour['reste'] = retour['total_ttc'] - retour['acompte']

        retour['acompte'] = round(retour['acompte'], 2)
        retour['acompte_ht'] = round(retour['acompte_ht'], 2)
        retour['reste'] = round(retour['reste'], 2)
        retour['total_ttc'] = round(retour['total_ttc'], 2)
        retour['total_ht'] = round(retour['total_ht'], 2)
        retour['prix_litre'] = round(retour['prix_litre'], 4)
        retour['livraison_ttc'] = round(retour['livraison_ttc'], 2)
        print retour
        return retour

    def creer_commande(self):
        valeur = self.valeur()
        livraison = TarifLivraison.objects.get(zone=self.zone, type_livraison=self.type_livraison)
        config = Config.objects.filter(actif=True)[0]
        c = Commande.objects.create(
            zone=self.zone,
            client=self.client,
            adresse_livraison=self.adresse_livraison,
            adresse_facturation=self.adresse_facturation,
            type_fioul=self.type_fioul,
            type_livraison=self.type_livraison,
            qte=self.qte,
            commentaire=self.commentaire,
            commission_ttc=valeur['acompte'],
            commission_ht=valeur['acompte_ht'],
            total_ttc=valeur['total_ttc'],
            total_ht=valeur['total_ht'],
            date_livraison=livraison.date_livraison(),
            panier_id=self.id,
            statut='2',
        )
        c.adresse_livraison.pk = None
        c.adresse_livraison.nom_adresse = 'commande'
        c.adresse_livraison.save()
        if c.adresse_facturation:
            c.adresse_facturation.pk = None
            c.adresse_facturation.nom_adresse = 'commande'
            c.adresse_facturation.save()
        c.save()
        c = Commande.objects.get(id=c.id)
        return c

    def set_client(self, client):
        self.client = client
        self.adresse_livraison = client.adresse_set.filter(nom_adresse='adresse_par_defaut')[0]
        factu = client.adresse_set.filter(nom_adresse='facturation')
        if factu:
            self.adresse_facturation = factu[0]
        self.save()



STATUTS_COMMANDE = (
    ('0', 'validée'),
    ('1', 'annulée'),
    ('2', 'en attente'),
)

class Commande(models.Model):
    zone = models.ForeignKey('Zone')
    client = models.ForeignKey('Client', null=True, blank=True)
    adresse_livraison = models.ForeignKey('Adresse', related_name='+', null=True, blank=True)
    adresse_facturation = models.ForeignKey('Adresse', related_name='+', null=True, blank=True)
    type_fioul = models.ForeignKey('TypeFioul', null=True, blank=True)
    type_livraison = models.ForeignKey('TypeLivraison', null=True, blank=True)
    qte = models.IntegerField(default=1000)
    commentaire = models.TextField(null=True, blank=True)
    commission_ttc = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    commission_ht = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    total_ht = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    livraison_ttc = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    date = models.DateTimeField(auto_now_add=True)
    date_livraison = models.DateField()
    statut = models.CharField(max_length=2, default='0', choices=STATUTS_COMMANDE)
    panier_id = models.IntegerField(null=True, blank=True)
    monetico_id = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.zone.nom

    def data(self):
        if self.livraison_ttc < 0:
            prix_livraison = '- %s' % localize(floatformat(-1 * self.livraison_ttc, '-2'))
        else:
            prix_livraison = '+ %s' % localize(floatformat(self.livraison_ttc, '-2'))


        d = {
            'client_nom' : self.adresse_livraison.nom,
            'client_prenom' : self.adresse_livraison.prenom,
            'commande_id' : self.id,
            'distributeur_email' : self.zone.email,
            'distributeur_tel' : self.zone.telephone,
            'distributeur_raison_sociale' : self.zone.raison_sociale,
            'distributeur_siret' : self.zone.siret,
            'distributeur_adresse' : self.zone.adresse,
            'distributeur_code_postal' : self.zone.code_postal,
            'livraison_adresse' : self.adresse_livraison.detail_1,
            'livraison_code_postal' : self.adresse_livraison.code_postal,
            'livraison_ville' : self.adresse_livraison.detail_4,
            'livraison_message' : self.commentaire,
            'client_telephone' : self.client.telephone,
            'qte' : self.qte,
            'prix_litre' : localize(floatformat(self.total_ttc / Decimal(self.qte), '-4')),
            'type_fioul' : self.type_fioul.nom,
            'type_livraison' : self.type_livraison.nom,
            'prix_livraison' : prix_livraison,
            'total_ttc' : localize(floatformat(self.total_ttc, '-2')),
            'acompte' : localize(floatformat(self.commission_ttc, '-2')),
            'reste' : localize(floatformat(self.get_reste_ttc(), '-2')),
            'date_livraison' : template_date(self.date_livraison, 'j F Y'),

            # '' : self.id,
        }
        return d

    def get_tva(self):
        return self.total_ttc - self.total_ht

    def get_commission_tva(self):
        return self.commission_ttc - self.commission_ht

    def get_reste_ttc(self):
        return self.total_ttc - self.commission_ttc

    def get_reste_ht(self):
        return self.total_ht - self.commission_ht

    def get_reste_tva(self):
        return self.get_tva() - self.get_commission_tva()

    def get_prix_litre(self):
        return self.total_ttc / Decimal(self.qte)

    def client_nom(self):
        return '%s %s' % (self.adresse_livraison.prenom, self.adresse_livraison.nom)

    def reste_ttc(self):
        return self.total_ttc - self.commission_ttc

class Message(models.Model):
    type = models.ForeignKey('TypeMessage')
    user = models.ForeignKey(User, blank=True, null=True)
    client = models.ForeignKey('Client', blank=True, null=True)
    commande = models.ForeignKey('Commande', blank=True, null=True)
    sujet = models.CharField(max_length=255)
    destinataire = models.CharField(max_length=255)
    data = models.TextField(blank=True, null=True)
    a_envoyer = models.BooleanField('à envoyer', default=True)
    envoye = models.BooleanField('envoyé', default=False)
    external_id = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return '{0} - {1}'.format(self.destinataire, self.sujet)

class TypeMessage(models.Model):
    nom = models.CharField(max_length=255)
    template_id = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.nom

class Prospect(models.Model):
    email = models.EmailField()
    code_postal = models.CharField('Code postal', max_length=10)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s (%s)' % (self.email, self.code_postal)
