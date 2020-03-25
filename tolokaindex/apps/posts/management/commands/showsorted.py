from urllib.parse import urlencode, quote

from django.core.management.base import BaseCommand
from django.db.models import Min, Max
from django.utils.timezone import now

from tolokaindex.apps.posts.models import Post, MediaItem


SEARCH_URL = 'https://toloka.to/tracker.php?nm='


class Command(BaseCommand):
    def handle(self, *args, **options):
        for number, post in reversed(list(enumerate(MediaItem.objects.filter(
                posts__isnull=False
        ).annotate(
            first_title=Min('posts__titles__title'),
            last_title=Max('posts__titles__title'),
            max_year=Max('posts__years__year'),
            max_registered_on=Max('posts__raw_post__registered_on'),
        ).order_by(
            '-max_year',
            '-max_registered_on',
            '-first_title'
        )[:100], 1))):
            print(
                f'{number:3} | '
                f'{post.first_title:40} | '
                f'{post.last_title:40} | '
                f'{post.max_year:9} | '
                f'{post.max_registered_on} | '
                f'{(now().date() - post.max_registered_on).days:11} | '
                f'{SEARCH_URL}{quote(post.first_title)}'
            )
        print('-' * 200)
        print(
            f'{"#":>3} | '
            f'{"First title":40} | '
            f'{"Last title":40} | '
            f'{"Last year":9} | '
            f'{"Registered":10} | '
            f'{"Days passed":11} | '
            f'{"Search URL"}'
        )
