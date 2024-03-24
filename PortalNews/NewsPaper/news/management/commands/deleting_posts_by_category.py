from django.core.management.base import BaseCommand

from news.models import Post, Category


class Command(BaseCommand):
    help = 'Deletes all posts from the selected categories.'

    def add_arguments(self, parser):
        parser.add_argument(
            'category',
            nargs='+',
            type=str,
            help='Write the category(s) from which you want to delete all entries. '
                 'If there are several categories, write them separated by a space',
        )
        parser.add_argument(
            '-l',
            '--list_category',
            help='Display a list of all available categories for cleaning',
        )
        parser.add_argument(
            '-y',
            '--yes',
            action='store_true',
            help='Confirm everything',
        )

    def handle(self, *args, **options):
        categories: str = options['category']
        confirm_all: bool = options['yes']
        list_category: bool = options['list_category']

        answer = None

        if categories:
            for category in categories:
                if Category.objects.filter(category=category):
                    filter_category = Post.objects.filter(categories__category=category)
                    len_queryset = len(list(filter_category))
                    if not confirm_all:
                        self.stdout.readable()
                        self.stdout.write(
                            self.style.ERROR(
                                f'Are you sure you want to delete {len_queryset} post(s) '
                                f'in the {category} category? '
                                f'This action cannot be undone!\n'
                                f'yes/no'
                            )
                        )
                        answer = input()

                    if answer == 'yes' or confirm_all:
                        filter_category.delete()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'{len_queryset} posts in the {category} category have been successfully deleted'
                            )
                        )
                    else:
                        self.stdout.write(self.style.ERROR('Access denied'))
                else:
                    self.stdout.write(f'There is no {category} category.')

        if list_category:
            categories_queryset = Category.objects.all()
            for category in categories_queryset:
                count_posts = Post.objects.filter(categories__category=category).count()
                self.stdout.write(f'{category}({count_posts})')
