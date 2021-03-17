from django.db.models import OuterRef, QuerySet, Subquery
from django.db.models.aggregates import Max
from django.http import HttpRequest
from django.utils.html import format_html
from public_admin.admin import PublicModelAdmin
from public_admin.sites import PublicAdminSite, PublicApp

from tolokaindex.apps.posts.models import MediaItem, Title
from tolokaindex.utils.langdetector import Language


class PublicMediaItemAdmin(PublicModelAdmin):
    list_display = ['title_ukr', 'title_not_ukr', 'max_year', 'max_registered_on', 'link']
    list_display_links = None
    search_fields = ['posts__titles__title']

    title_ukr_query = Title.objects.filter(post__media_item=OuterRef('pk'), language=Language.UKR).values('title')
    title_eng_query = Title.objects.filter(post__media_item=OuterRef('pk'), language=Language.ENG).values('title')
    title_not_ukr_query = Title.objects.filter(post__media_item=OuterRef('pk')).exclude(language=Language.UKR) \
        .values('title')

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(
            title_ukr=Subquery(self.title_ukr_query[:1]),
            title_eng=Subquery(self.title_eng_query[:1]),
            title_not_ukr=Subquery(self.title_not_ukr_query),
            max_year=Max('posts__years__year'),
            max_registered_on=Max('posts__raw_post__registered_on'),
        ).order_by(
            '-max_year',
            '-max_registered_on',
            'title_ukr'
        ).exclude(
            title_ukr=None,
            title_not_ukr=None,
        )

    def title_ukr(self, obj) -> str:
        return obj.title_ukr

    def title_not_ukr(self, obj) -> str:
        return obj.title_eng or obj.title_not_ukr

    def max_year(self, obj):
        return obj.max_year

    max_year.admin_order_field = 'max_year'

    def max_registered_on(self, obj):
        return obj.max_registered_on

    max_registered_on.admin_order_field = 'max_registered_on'

    def link(self, obj):
        return format_html(
            f"<a href='https://toloka.to/tracker.php?nm={obj.title_eng or obj.title_ukr}' target='_blank'>link</a>"
        )


public_app = PublicApp("posts", models=("MediaItem",))
public_admin = PublicAdminSite("dashboard", public_app)
public_admin.register(MediaItem, PublicMediaItemAdmin)
