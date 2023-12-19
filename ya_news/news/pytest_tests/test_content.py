import pytest

from django.conf import settings
from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_record_on_page(client, home_url, create_news):
    response = client.get(home_url)
    assert response.context['object_list'].count(
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url, create_news):
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(reader_client, news, detail_url, create_comment):
    response = reader_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = list(news.comment_set.all())
    assert all_comments == sorted(
        all_comments,
        key=lambda comment: comment.created
    )


def test_form_for_anonymous_user(client, edit_url):
    response = client.get(edit_url)
    if response.context is not None:
        assert 'form' not in response.context


def test_form_for_users(author_client, edit_url):
    response = author_client.get(edit_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
