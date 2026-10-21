import os
from django.core.wsgi import get_wsgi_application

# This call serves to set the default settings module for the WSGI server.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()