#wsgi serving script
import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['PYTHON_EGG_CACHE'] = '/var/cache/www/pythoneggs'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
