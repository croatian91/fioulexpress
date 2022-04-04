from django import test
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from subprocess import call

# Create your tests here.
from .models import *
from contenu.models import *


# class CodePostalTestCase(test.TestCase):
#     def setUp(self):
#         zone = Zone.objects.create(nom="Paris")
#         CodePostal.objects.create(code_postal="75001", commune="Paris 01", zone=zone)
#         CodePostal.objects.create(code_postal="75002", commune="Paris 02", zone=zone)
#
#     def test_codepostal_setup(self):
#         print 'test_codepostal_setup'
#         paris_1 = CodePostal.objects.get(code_postal="75001", commune="Paris 01")
#         paris_2 = CodePostal.objects.get(code_postal="75002", commune="Paris 02")
#         zone = Zone.objects.get(nom="Paris")
#         self.assertEqual(paris_1.code_postal, "75001")
#         self.assertEqual(paris_2.code_postal, "75002")
#         self.assertEqual(paris_2.zone.id, zone.id)
#         self.assertEqual(zone.codepostal_set.count(), 2)
#
#     def test_create_distrib(self):
#         print 'test_create_distrib'
#         distrib = Distributeur.objects.create(nom='Distrib 1')
#         distrib.save()
#         print Distributeur.objects.all()
#         zone = Zone.objects.get(nom="Paris")
#         zone.distributeur = distrib
#         zone.save()
#
#     def test_distrib_cp(self):
#         print 'test_distrib_cp'
#         print Distributeur.objects.all()
#         cp = CodePostal.objects.filter(zone__distributeur=Distributeur.objects.all()[0])
#         self.assertEqual(cp.count(), 2)


class CasperTests(StaticLiveServerTestCase):
    def setUp(self):
        # settings.DEBUG = True
        Config.objects.create(commission=Decimal("0.1"), actif=True)

        Page.objects.create(titre="Qui sommes nous", adresse="qui-sommes-nous")

        distributeur = Distributeur.objects.create(nom="Distrib 1")
        zone = Zone.objects.create(nom="Paris", distributeur=distributeur)
        zone.jours_livraison = ["0", "1", "2", "3", "4", "5"]
        zone.types_paiement = ["0", "1", "2"]
        zone.save()

        fioul_ordinaire = TypeFioul.objects.create(nom="Fioul ordinaire")
        TarifFioul.objects.create(zone=zone, type_fioul=fioul_ordinaire, prix_ttc=550)

        livraison_express = TypeLivraison.objects.create(nom="Express")
        TarifLivraison.objects.create(
            zone=zone, type_livraison=livraison_express, extra=10
        )

        TarifDecote.objects.create(zone=zone, min=500, max=999, decote=-10)
        TarifDecote.objects.create(zone=zone, min=1000, max=1999, decote=0)
        TarifDecote.objects.create(zone=zone, min=2000, max=2999, decote=0)
        TarifDecote.objects.create(zone=zone, min=3000, max=3999, decote=0)
        TarifDecote.objects.create(zone=zone, min=4000, max=4999, decote=0)
        TarifDecote.objects.create(zone=zone, min=5000, max=10000, decote=0)

        CodePostal.objects.create(code_postal="75001", commune="Paris 01", zone=zone)
        CodePostal.objects.create(code_postal="75002", commune="Paris 02", zone=zone)

    def test_casper_sequence(self):
        self.assertEqual(
            call(
                [
                    "casperjs",
                    "--base_url=" + self.live_server_url,
                    "test",
                    "/home/matt/dev/fioul/test/base.js",
                ]
            ).real,
            0,
        )
        print(Client.objects.all())
