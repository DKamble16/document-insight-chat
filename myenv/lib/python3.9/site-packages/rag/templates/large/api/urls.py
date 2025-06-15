from django.views.decorators.csrf import csrf_exempt
from rag import rest
from .routes import messages


urls = [
    # authentication
    rest('ping', 'GET', messages.ping, [csrf_exempt]),
    rest('echo', 'POST', messages.echo, [csrf_exempt]),
]
