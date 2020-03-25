import logging

from django.core.management.base import BaseCommand

from tolokaindex.apps.posts.models import Post
from tolokaindex.apps.raw_posts.models import RawPost


class Command(BaseCommand):
    def handle(self, *args, **options):
        number = 0
        for number, raw_post in enumerate(RawPost.objects.order_by('-registered_on').all(), 1):
            if number % 100 == 0:
                logging.info(f'Processed: {number}')

            try:
                Post.update_from_raw(raw_post)

            except Exception as exception:
                logging.warning(f'Wrong: {raw_post.title}. Error: {exception}')

        logging.info(f'Processed: {number}')
