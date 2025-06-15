# pylint: skip-file
import os

# set environment
ENVIRONMENT = os.environ.get('RAG_ENV', 'production').lower()
if os.environ.get('RAG_TESTING'):
    ENVIRONMENT = 'testing'

# select settings
if ENVIRONMENT == 'development':
    from .development import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    from .production import *
