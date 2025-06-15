from rag.cli.command  import BaseCommand


class Command(BaseCommand):

    help = 'Show application settings'

    # def add_arguments(self, parser):
    #     parser.add_argument('name', type=str, help='project name / directory to create')

    def execute(self, args):
        print('settings')
