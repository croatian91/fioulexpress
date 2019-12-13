import hmac, hashlib
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
        'version' : '3.0',
        'TPE' : settings.MONETICO_TPE,
        'date' : datetime.now().strftime("%d/%m/%Y:%H:%M:%S"),
        'montant' : '%sEUR' % panier.valeur()['acompte'],
        # 'montant_a_capturer' : '%dEUR' % panier.valeur()['acompte'],
        # 'montant_deja_capture' : '0EUR',
        # 'montant_restant' : '0EUR',
        'reference' : str(panier.id),
        'texte-libre' : texte_libre.encode('ascii', 'replace'),
        'mail' : panier.client.email,
        'lgue' : 'FR',
        'societe' : settings.MONETICO_SOCIETE,
        'url_retour' : 'https://%s/commande/paiement/' % request.META['HTTP_HOST'],
        'url_retour_ok' : 'https://%s/commande/monetico_ok/' % request.META['HTTP_HOST'],
        'url_retour_ko' : 'https://%s/commande/monetico_ko/' % request.META['HTTP_HOST'],
        'MAC' : '',
        'options' : '',
        'mode_affichage' : 'iframe',
    }

    # sceau_tpl = '{TPE:s}*{date:s}*{montant_a_capturer:s}{montant_deja_capture:s}{montant_restant:s}*{reference:s}*{texte-libre:s}*{version:s}*{lgue:s}*{societe:s}*'
    sceau_tpl = u'{TPE:s}*{date:s}*{montant:s}*{reference:s}*{texte-libre:s}*{version:s}*{lgue:s}*{societe:s}*{mail:s}**********'
    sceau = sceau_tpl.format(**data)

    mac = hmac.HMAC(operation_key(settings.MONETICO_CLE), None, hashlib.sha1)
    mac.update(sceau.encode('iso8859-1'))
    data['MAC'] = mac.hexdigest()

    return settings.MONETICO_URL + '?' + urlencode(data)
