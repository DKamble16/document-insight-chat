from django.db.models import *

# override base model class to add additional functionality
def lazy_model(cache={}):
    if 'Model' not in cache:
        from .model import Model
        cache['Model'] = Model
    return cache['Model']

# lazily evaluate the modified base model class otherwise importing rag.models (like in rag's __init__.py)
# raises an django.core.exceptions.ImproperlyConfigured because we are using the base models meta class
del globals()['Model']
def __getattr__(name):
    if name == "Model": return lazy_model()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
