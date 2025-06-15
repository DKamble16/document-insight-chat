# register a command
def register(name, command, subparsers):
    parser = subparsers.add_parser(name, help=command.help)
    parser.set_defaults(cmd=command.execute)
    command.add_arguments(parser)
