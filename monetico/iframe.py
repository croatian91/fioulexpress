import hmac, hashlib
import json
from encodings import hex_codec

from django.conf import settings
from django.utils.datetime_safe import datetime
from django.utils.http import urlencode

def operation_key(key) :

        hexStrKey = key[0:38]
        hexFinal = key[38:40] + "00";

        cca0 = ord(hexFinal[0:1])

        if cca0 > 70 and cca0 < 97 :
                hexStrKey += chr(cca0 - 23) + hexFinal[1:2]
        elif hexFinal[1:2] == "M" :
                hexStrKey += hexFinal[0:1] + "0"
        else :
                hexStrKey += hexFinal[0:2]
        c = hex_codec.Codec()
        return c.decode(hexStrKey)[0]

def get_iframe_src(panier, request):
    texte_libre = '%s %s %s' % (panier.adresse_livraison.prenom, panier.adresse_livraison.nom, panier.client.email)
    data = {
        'TPE': settings.MONETICO_TPE,
        "contexte_commande": json.dumps(
            {'billing':
                 {
                     'addressLine1': panier.adresse_livraison.detail_1,
                     'city': panier.adresse_livraison.detail_4,
                     'postalCode': panier.adresse_livraison.code_postal,
                     'country': panier.adresse_livraison.pays,
                 },
            },
        ),
        'date': datetime.now().strftime("%d/%m/%Y:%H:%M:%S"),
        'lgue': 'FR',
        'mail': panier.client.email,
        'mode_affichage': 'iframe',
        'montant': '%sEUR' % panier.valeur()['acompte'],
        'reference': str(panier.id),
        'societe': settings.MONETICO_SOCIETE,
        'texte-libre': texte_libre,
        'url_retour_err': 'https://%s/commande/monetico_ko/' % request.META['HTTP_HOST'],
        'url_retour_ok': 'https://%s/commande/monetico_ok/' % request.META['HTTP_HOST'],
        'version': '3.0',
    }

    sceau_tpl = 'TPE={TPE:s}*contexte_commande={contexte_commande:s}*date={date:s}*lgue={lgue:s}*mail={mail:s}*mode_affichage={mode_affichage:s}*montant={montant:s}*reference={reference:s}*societe={societe:s}*texte-libre={texte-libre:s}*url_retour_err={url_retour_err:s}*url_retour_ok={url_retour_ok:s}*version={version:s}'
    sceau = sceau_tpl.format(**data)
    print("DEBUG", sceau)
    mac = hmac.HMAC(operation_key(settings.MONETICO_CLE), None, hashlib.sha1)
    mac.update(sceau.encode('iso8859-1'))
    data['MAC'] = mac.hexdigest()
    print("DEBUG", urlencode(data))
    return settings.MONETICO_URL + '?' + urlencode(data)
