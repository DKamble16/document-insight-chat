from rag.core import utils


# rag command patterned after django command
class BaseCommand:
    help = ''

    def add_arguments(self, parser):
        pass

    def execute(self, args):
        pass

# mixin that enables us to execute django commands from rag command line
class DjangoCommand():

    def execute(self, args):
        utils.import_root_module()
        options = vars(args)
        args = options.pop('args', ())
        base_options = {'verbosity': 1, 'force_color': False, 'no_color': False, 'skip_checks': False}
        super().execute(*args, **{**options, **base_options})
