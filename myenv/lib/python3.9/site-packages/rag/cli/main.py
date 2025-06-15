import os
import sys
import argparse
from . import commands


# register a command
def register(name, command, subparsers):
    parser = subparsers.add_parser(name, help=command.help)
    parser.set_defaults(cmd=command.execute)
    command.add_arguments(parser)


# main
def main():
    # set environment variable if we are running tests
    if len(sys.argv) >= 2 and sys.argv[1] == 'test':
        os.environ['RAG_TESTING'] = 'yes'

    # arguments
    parser = argparse.ArgumentParser(description='')
    subparsers = parser.add_subparsers(help='')

    # register all commands from commands package (see commands __init__)
    for name in [m for m in dir(commands) if not m.startswith('__')]:
        command = getattr(commands, name).Command()
        register(name, command, subparsers)

    # parse cli arguments and execute command
    try:
        # hijack the command line and run django's default manage.py script if manage is the second argument
        if commands.manage.inject(): return

        # parse args and execute command
        args = parser.parse_args()
        if hasattr(args, 'cmd'):
            sys.exit(args.cmd(args))
        else:
            parser.print_help()
    except ModuleNotFoundError as exc:
        if "No module named 'settings'" not in str(exc): raise exc
        print('Warning: Unable to detect rag/django project in current directory. Failed to load settings.')
