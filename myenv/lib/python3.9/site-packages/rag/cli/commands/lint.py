import os
import sys
import glob
import pylint.lint
from subprocess import call
from rag.cli.command  import BaseCommand
from rag.core.utils import find_root_module
from .test import watch


def contains_python(path, dir):
    if path.startswith('.'):
        return False
    if os.path.isfile(os.path.join(dir, path)):
        return path.endswith('.py')
    return len(glob.glob(os.path.join(dir, path) + '/**/*.py', recursive=True)) > 0

def find_python_paths():
    cwd = os.path.abspath(os.getcwd())
    files = os.listdir(cwd)
    return [f for f in files if contains_python(f, cwd)]


class Command(BaseCommand):

    help = 'Run pylint on current project with default or specified options'

    def add_arguments(self, parser):
        parser.add_argument('-w', '--watch', action='store_true', help='rerun linter when files change')
        parser.add_argument('options', nargs='*', help='run pylint with specified options')

    def execute(self, args):
        # setup args
        roots = find_python_paths()
        argv = args.options or ['--output-format=colorized', '--reports=no', *roots]

        # add current directory to path
        cwd = os.path.abspath(os.getcwd())
        sys.path.append(cwd)

        # run tests (with or without watcher)
        if args.watch:
            return watch(lambda: call([arg for arg in sys.argv if arg not in ['-w', '--watch']]))
        return pylint.lint.Run(argv)
