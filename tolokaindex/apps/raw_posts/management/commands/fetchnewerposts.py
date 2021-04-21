from django.core.management.base import BaseCommand

from tolokaindex.apps.raw_posts.grabbers import ListResultGrabber, SEARCH_NEWER_SERIES_URL, \
    SEARCH_NEWER_HD_SERIES_URL


class Command(BaseCommand):
    def handle(self, *args, **options):
        for url in (SEARCH_NEWER_SERIES_URL, SEARCH_NEWER_HD_SERIES_URL):
            grabber = ListResultGrabber(url)
            grabber.fetch_newer()

            print('Updates:', grabber.updates)
