from rag.core import utils
from rag.cli.command  import BaseCommand


class Command(BaseCommand):

    help = 'Run a python script in the application context'

    def add_arguments(self, parser):
        parser.add_argument('script', type=str, help='script file name')

    def execute(self, args):
        utils.import_root_module()
        with open(args.script, 'rb') as file:
            exec(compile(file.read(), args.script, 'exec'), {
                "__file__": args.script,
                "__name__": "__main__",
            })
