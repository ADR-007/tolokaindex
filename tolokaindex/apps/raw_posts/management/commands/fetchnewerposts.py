import logging

from django.core.management.base import BaseCommand, CommandError

from tolokaindex.apps.raw_posts.grabbers import SearchResultGrabber, ListResultGrabber


class Command(BaseCommand):
    def handle(self, *args, **options):
        grabber = ListResultGrabber()
        grabber.fetch_newer()
        print('Updates:', grabber.updates)
