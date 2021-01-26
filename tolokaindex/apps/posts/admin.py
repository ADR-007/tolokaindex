from django.db.models import QuerySet
from django.db.models.aggregates import Max, Min
from django.http import HttpRequest
from public_admin.admin import PublicModelAdmin
from public_admin.sites import PublicAdminSite, PublicApp

from tolokaindex.apps.posts.models import MediaItem


class MediaItemAdmin(PublicModelAdmin):
    list_display = ['first_title', 'last_title', 'max_year', 'max_registered_on']

    # ordering = ['-max_year', '-max_registered_on', '-first_title']

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(
            first_title=Min('posts__titles__title'),
            last_title=Max('posts__titles__title'),
            max_year=Max('posts__years__year'),
            max_registered_on=Max('posts__raw_post__registered_on'),
        ).order_by(
            '-max_year',
            '-max_registered_on',
            '-first_title'
        )

    def first_title(self, obj):
        return obj.first_title

    def last_title(self, obj):
        return obj.last_title

    def max_year(self, obj):
        return obj.max_year

    def max_registered_on(self, obj):
        return obj.max_registered_on


public_app = PublicApp("posts", models=("MediaItem",))
public_admin = PublicAdminSite("dashboard", public_app)
public_admin.register(MediaItem, MediaItemAdmin)
