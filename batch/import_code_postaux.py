import os, sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0]))))
os.environ["DJANGO_SETTINGS_MODULE"] = "fioul.settings"

import django

django.setup()

from django.conf import settings
from fioulexpress.models import *

from django.db import transaction


# transaction.set_autocommit(False)
for ligne in open("/tmp/zone.csv").readlines()[1:]:
    l = ligne.split(",")
    z, c = CodePostal.objects.get_or_create(code_postal=l[1], commune=l[0])
# transaction.commit()
print(l)
