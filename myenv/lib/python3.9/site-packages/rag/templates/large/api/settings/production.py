import os


DEBUG = False
SECRET_KEY = 'mysecret'
BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_PATH, '../production.sqlite3'),
    }
}
