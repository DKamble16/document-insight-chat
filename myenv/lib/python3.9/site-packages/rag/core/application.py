import os
import importlib
from django.apps import apps
from django.conf import settings
from django.urls import set_script_prefix
from django.utils.log import configure_logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from rag import rest
from rag.core.settings import default
from rag.core.utils import find_asgi_path


class Urls:
    def __init__(self, source):
        self.source = source or []
        self.urlpatterns = []
        self.restpatterns = []

    def add(self, urls):
        if not isinstance(urls, list):
            urls = [urls]
        self.restpatterns.extend(urls)

    def setup(self):
        if isinstance(self.source, str):
            if ':' in self.source:
                module, attribute = self.source.split(':')
            else:
                module, attribute = [self.source, 'urls']
            urls = getattr(importlib.import_module(module), attribute)
            self.add(urls)
        else:
            self.add(self.source)

class Application:

    def __init__(self, application, settings=None, urls=None, app=None):
        self.app = application
        self.settings = settings
        self.urls = Urls(urls)
        self.setup()

    def route(self, route, method, *args, **kwargs):
        def decorator(func):
            self.urls.add(rest(route, method, func, *args, **kwargs))
            func.routed = True
            return func
        return decorator

    def setup(self, set_prefix=True):
        # don't allow DJANGO_SETTINGS_MODULE because it loads settings differently than settings.configure (see dj docs)
        if "DJANGO_SETTINGS_MODULE" in os.environ:
            raise RuntimeError('DJANGO_SETTINGS_MODULE environment variable is not supported.')

        # load settings
        if isinstance(self.settings, str):
            module = importlib.import_module(self.settings)
            self.settings = {k: getattr(module, k) for k in dir(module) if not k.startswith('_') and k.isupper()}

        # inject urls into settings
        self.settings['ROOT_URLCONF'] = self.urls

        # inject root asgi app setting
        if 'ASGI_APPLICATION' not in self.settings:
            self.settings['ASGI_APPLICATION'] = find_asgi_path()

        # set default migrations module
        if 'MIGRATIONS_MODULES' not in self.settings and importlib.util.find_spec('migrations'):
            self.settings['MIGRATION_MODULES'] = {self.app: 'migrations'}

        # add this application to installed apps
        self.settings['INSTALLED_APPS'] = [self.app] + self.settings.get('INSTALLED_APPS', default.INSTALLED_APPS)

        # configure settings
        settings.configure(default, **self.settings)

        # configure logging
        configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)

        # set prefix
        if set_prefix:
            set_script_prefix('/' if settings.FORCE_SCRIPT_NAME is None else settings.FORCE_SCRIPT_NAME)

        # populate apps
        apps.populate(settings.INSTALLED_APPS)

        # setup urls
        self.urls.setup()

    @property
    def router(self):
        # websocketpatterns = signals.patterns
        return ProtocolTypeRouter({
            "http": get_asgi_application(), # may not be needed (http->django views is added by default)
            # 'websocket': URLRouter(urls.websocketpatterns),
        })
