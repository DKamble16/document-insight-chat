import os
from rag import Application
from django.views.decorators.csrf import csrf_exempt


# settings
environment = os.environ.get('RAG_ENV', 'development')
settings = {}
settings['DEBUG'] = environment == 'development'
settings['SECRET_KEY'] = os.environ['DJANGO_SECRET'] if environment == 'production' else ''

# application
app = Application(__name__, settings)

# routes
@app.route('', 'GET')
def hello(request):
    return {'data': 'hello world!'}

@app.route('echo', 'POST', [csrf_exempt])
def echo(request):
    return request.data
