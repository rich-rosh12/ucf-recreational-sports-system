import os
from django.core.asgi import get_asgi_application

# This variable serves to set the default settings module for the ASGI asynchronous server.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()