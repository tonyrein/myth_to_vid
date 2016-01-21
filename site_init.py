import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myth_to_vid.settings'
import django

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


# Initialize list of Orphan objects:
from utils.myth import initialize_orphans_list, make_video_samples
num_orphans = initialize_orphans_list(override=True)
res = make_video_samples()

