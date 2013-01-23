import os
import sys
import site

import settings


site.addsitedir("/opt/rpi-django/django/env/lib/python2.7/site-packages")
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
