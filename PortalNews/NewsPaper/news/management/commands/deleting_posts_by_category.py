from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = ''
    missing_args_message = ''

    def add_arguments(self, parser):
        parser.add_argument('category', nargs='+', type=str)
        parser.add_argument('--list-category')

    def handle(self, *args, **options):
