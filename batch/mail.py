import os
import sys
import requests

import django

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0]))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'fioul.settings'

django.setup()

from fioulexpress.models import *


def main():

    config = Config.objects.filter(actif=True)[0]

    for msg in Message.objects.filter(a_envoyer=True, envoye=False):
        destinataire = msg.destinataire
        sujet = msg.sujet
        if getattr(settings, 'DEBUG_EMAIL', False):
            destinataire = settings.FIOUL_DEBUG_EMAIL
            sujet += ' / TEST : ' + msg.destinataire
        data = {
            'FromEmail':config.email_admin,
            'FromName':settings.FIOUL_CONTACT_NAME,
            'Recipients': [
                {'Email':destinataire},
            ],
            'Subject':sujet,
            'Mj-TemplateID' : msg.type.template_id,
            'Mj-TemplateLanguage' : True,
            'Vars' : json.loads(msg.data),
        }
        r = requests.post(settings.FIOUL_MJ_URL, auth=(settings.FIOUL_MJ_USER, settings.FIOUL_MJ_PASS), json=data)
        if r.status_code == 200:
            msg.external_id = r.json().get('Sent', [{}])[0].get('MessageID', '')
            msg.envoye = True
            msg.save()


if __name__ == '__main__':
    main()
