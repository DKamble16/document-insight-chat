from rag import rest
from django.views.decorators.csrf import csrf_exempt
from .controllers import create_message, get_message, index_messages, update_message, destroy_message


urls = [
    rest('messages', 'POST', create_message, [csrf_exempt]),
    rest('messages/<int:id>', 'GET', get_message),
    rest('messages', 'GET', index_messages),
    rest('messages/<int:id>', 'PUT', update_message, [csrf_exempt]),
    rest('messages/<int:id>', 'DELETE', destroy_message, [csrf_exempt]),
]
