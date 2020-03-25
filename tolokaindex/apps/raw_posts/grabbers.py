from datetime import date
from itertools import islice, count
from typing import Optional, Iterable, Any
from urllib.parse import urlparse

import requests
from django.db.transaction import atomic
from lxml import html
from lxml import etree

from tolokaindex.apps.raw_posts.models import RawPost


SEARCH_NEWER_URL = 'https://toloka.to/f32?sort=8'


class ResultGrabber:
    rows_xpath: str = None
    next_page_xpath: str = None
    title_element_xpath: str = None
    title_registered_on_xpath: str = None

    min_date = date(year=2010, month=1, day=1)

    def __init__(self, url: str = None):
        self.url = url or SEARCH_NEWER_URL
        self.updates = 0
        self.session = requests.session()
        self.session.max_redirects = 0

    @atomic
    def fetch_newer(self) -> None:
        page_url = self.url

        for page in count(1):
            print(f'Page #{page:3} ' + '-' * 100)
            page_url = self.process_page(page_url)

            if not page_url:
                break

    def process_page(self, url: str) -> Optional[str]:
        response = self.session.get(url)
        response.raise_for_status()

        tree = html.fromstring(response.text)

        for row in self.get_result_rows(tree):
            try:
                updated = self.store_row_in_db(row)

                if not updated:
                    return

            except IndexError:
                pass

        return self.get_next_page_url(tree)

    def store_row_in_db(self, row: html.HtmlElement) -> bool:
        title_element = row.xpath(self.title_element_xpath)[0]
        post_id = title_element.attrib['href']
        title = title_element.text
        registered_on = date.fromisoformat(row.xpath(self.title_registered_on_xpath)[0].text)

        row_data = etree.tounicode(row)

        post: Optional[RawPost] = RawPost.objects.filter(post_id=post_id).first()

        if post and post.registered_on == registered_on:
            return False

        RawPost.objects.update_or_create(
            defaults=dict(
                registered_on=registered_on,
                title=title,
                row=row_data,
            ),
            post_id=post_id,
        )

        self.updates += 1

        print(f'Added: {title}')

        if registered_on < self.min_date:
            print('Too early posts... stop.')
            return False

        return True

    def get_next_page_url(self, tree: html.HtmlElement) -> Optional[str]:
        elements = tree.xpath(self.next_page_xpath)

        if not elements:
            return None

        parsed = urlparse(self.url)
        return '{}://{}/{}'.format(parsed.scheme, parsed.netloc, elements[0].attrib['href'])

    @classmethod
    def get_result_rows(cls, tree: html.HtmlElement) -> Iterable[html.HtmlElement]:
        return tree.xpath(cls.rows_xpath)[1:]


class SearchResultGrabber(ResultGrabber):
    rows_xpath = '//*[@id="form"]/table[3]/tr'
    title_element_xpath = 'td[@class="topictitle genmed"]/a'
    title_registered_on_xpath = 'td[@title="Написане"]'
    next_page_xpath = '//*[@id="form"]/table[4]/tr/td[2]/span/a[5]'


class ListResultGrabber(ResultGrabber):
    rows_xpath = '//*/table[@class="forumline"][1]/tr'
    title_element_xpath = 'td/span[@class="topictitle"]/a'
    title_registered_on_xpath = 'td[5]/span[@class="gensmall"]'
    next_page_xpath = '//*/span/a[text()="наступна"]'
