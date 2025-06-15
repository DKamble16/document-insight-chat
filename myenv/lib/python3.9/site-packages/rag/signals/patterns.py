from django.urls import path
from .consumer import SignalConsumer


patterns = [
    path(r'ws/signals', SignalConsumer),
]
