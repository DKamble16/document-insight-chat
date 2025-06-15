import os
from rag import Application
from rag import models, abort, validate, v
from django.views.decorators.csrf import csrf_exempt


# settings
ENVIRONMENT = os.environ.get('RAG_ENV', 'development')
DEBUG = (ENVIRONMENT == 'development')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': f'{ENVIRONMENT}.sqlite3',
    }
}
SECRET_KEY = os.environ['DJANGO_SECRET'] if ENVIRONMENT == 'production' else ''
