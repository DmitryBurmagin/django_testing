import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_record_on_page(client, create_news):
    url = reverse('news:home')
    response = client.get(url)
    assert len(response.context['object_list']) == 10


def test_news_order(client, create_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(reader_client, create_comment):
    news, detail_url, comment = create_comment
    url = reverse('news:detail', args=(news.pk,))
    response = reader_client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


def test_form_for_anonymous_user(client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = client.get(url)
    if response.context is not None:
        assert 'form' not in response.context
    else:
        assert True


def test_form_for_users(author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = author_client.get(url)
    assert 'form' in response.context
