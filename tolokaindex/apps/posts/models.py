import logging
import re
from typing import List, Tuple

from django.db import models
from django.utils.functional import cached_property

from tolokaindex.apps.raw_posts.models import RawPost
from tolokaindex.utils.langdetector import detect_language

logger = logging.getLogger(__name__)

TITLE_RE = re.compile(
    r'^(\[.*?\])?'
    r'(?P<title>.*?)'
    r'\((?P<years>((\d{4})( ?- ?(\d{2,4}))?(, )?)+)\)'
)
TITLE_EXTRA_INFO = re.compile(r'\(.*?\)')
TITLE_MAX_LENGTH = 500

TITLE_SEASON_RE = re.compile(
    r'\(сезони? (?P<seasons>\d+(-\d+)?).*?\)',
    flags=re.IGNORECASE
)


class Title(models.Model):
    title = models.CharField(max_length=TITLE_MAX_LENGTH, unique=True)
    language = models.CharField(max_length=100, null=True, default=None)

    def save(self, *args, **kwargs) -> None:
        if self.language is None:
            self.language = detect_language(self.title)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.title)


class Year(models.Model):
    year = models.PositiveIntegerField(unique=True)

    def __str__(self) -> str:
        return str(self.year)


class MediaItem(models.Model):
    @cached_property
    def titles(self) -> Tuple[str, ...]:
        return tuple(self.posts.values_list('titles__title', flat=True).distinct())

    @cached_property
    def years(self) -> Tuple[str, ...]:
        return tuple(self.posts.values_list('years__year', flat=True).distinct())

    def __str__(self) -> str:
        return f'Titles: {self.titles}, years: {self.years}'


class Post(models.Model):
    raw_post = models.ForeignKey(RawPost, on_delete=models.CASCADE)

    titles = models.ManyToManyField(Title)
    years = models.ManyToManyField(Year)

    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name='posts')

    @classmethod
    def update_from_raw(cls, raw_post: RawPost) -> 'Post':
        raw_title = raw_post.title.replace('–', '-')
        re_result = TITLE_RE.search(raw_title)
        titles = cls._parse_titles(re_result.group('title'))
        years = cls._parse_years(re_result.group('years'))
        seasons = cls._parse_seasons(raw_title)

        for title in titles:
            Title.objects.update_or_create(title=title)

        Year.objects.bulk_create([Year(year=year) for year in years], ignore_conflicts=True)
        titles_models = Title.objects.filter(title__in=titles)
        years_models = Year.objects.filter(year__in=years)

        post, _ = cls.objects.update_or_create(raw_post=raw_post, defaults=dict(
            media_item=cls._get_media_item(titles_models, years_models)
        ))
        post.titles.set(titles_models)
        post.years.set(years_models)
        post.seasons.set([PostSeason(season=season) for season in seasons], bulk=False)

        return post

    @staticmethod
    def _parse_titles(title_str: str) -> List[str]:
        titles = []

        for title in title_str.split('/'):
            titles.append(TITLE_EXTRA_INFO.sub('', title).strip())

        return titles

    @staticmethod
    def _parse_years(years_str: str) -> List[int]:
        years = Post._parse_sequence(years_str)

        return years

    @staticmethod
    def _parse_sequence(sequence_str: str) -> List[int]:
        values = []

        for values_range_str in sequence_str.split(','):
            values_range = values_range_str.split('-')

            range_start = range_end = int(values_range[0])

            if len(values_range) > 1:
                range_end = int(values_range[1])

            for value in range(range_start, range_end + 1):
                values.append(value)

        return values

    @classmethod
    def _get_media_item(cls, titles: List[Title], years: List[Year]) -> MediaItem:
        queryset = MediaItem.objects.distinct().filter(
            posts__titles__in=titles,
            posts__years__in=years
        )

        try:
            return queryset.get()

        except MediaItem.DoesNotExist:
            logger.info(f'New media item: {titles}: {years}')
            return MediaItem.objects.create()

        except MediaItem.MultipleObjectsReturned:
            logger.debug(f'Multiple media items exists for titles: {titles}, years: {years}')

            media_items = list(queryset)
            first_item = media_items.pop(0)

            Post.objects.filter(media_item__in=media_items).update(media_item=first_item)

            return first_item

    @classmethod
    def _parse_seasons(cls, raw_title: str) -> List[int]:
        results = TITLE_SEASON_RE.search(raw_title)

        if not results:
            return []

        seasons_str = results.group('seasons')

        return cls._parse_sequence(seasons_str)


class PostSeason(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='seasons')
    season = models.PositiveIntegerField()


class PostSeries(models.Model):
    season = models.ForeignKey(PostSeason, on_delete=models.CASCADE, related_name='series')
    series = models.PositiveIntegerField()
