import sys
from subprocess import call
from rag.cli.command import BaseCommand
from rag.core.utils import find_asgi_path


class Command(BaseCommand):

    help = 'Serve the application via daphne'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--port', default='8000', help='port to listen to')
        parser.add_argument('-b', '--bind', default='0.0.0.0', help='host to bind to')
        parser.add_argument('-a', '--application', default=None, help='asgi application module path')

    def execute(self, args):
        if not args.application:
            args.application = find_asgi_path()
        try:
            sys.exit(call(f'daphne -p {args.port} -b {args.bind} {args.application}', shell=True))
        except KeyboardInterrupt:
            pass
