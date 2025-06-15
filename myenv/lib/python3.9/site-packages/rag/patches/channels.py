import channels.routing



def get_default_application():
    import importlib
    from django.core.exceptions import ImproperlyConfigured
    from django.conf import settings
    from functools import reduce
    """
    Gets the default application, set in the ASGI_APPLICATION setting.
    """
    try:
        if ":" in settings.ASGI_APPLICATION:
            path, name = settings.ASGI_APPLICATION.split(":")
        else:
            path, name = settings.ASGI_APPLICATION.rsplit(".", 1)
    except (ValueError, AttributeError):
        raise ImproperlyConfigured("Cannot find ASGI_APPLICATION setting.")
    try:
        module = importlib.import_module(path)
    except ImportError:
        raise ImproperlyConfigured("Cannot import ASGI_APPLICATION module %r" % path)
    try:
        value = reduce(lambda m, v: getattr(m, v), name.split('.'), module)
    except AttributeError:
        raise ImproperlyConfigured(
            "Cannot find %r in ASGI_APPLICATION module %s" % (name, path)
        )
    return value

channels.routing.get_default_application = get_default_application
