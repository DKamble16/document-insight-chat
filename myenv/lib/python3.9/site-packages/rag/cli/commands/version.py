from rag.cli.command  import BaseCommand
try:
    from importlib import metadata
except ImportError: # for Python<3.8
    import importlib_metadata as metadata


def get_version():
    return metadata.version('rag')

class Command(BaseCommand):

    help = 'Display current Rag version'

    def execute(self, args):
        print(get_version())
