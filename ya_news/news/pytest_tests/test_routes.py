from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_home_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_news_detail_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, parametrized_client, expected_status',
    (
        ('news:edit', pytest.lazy_fixture('client'),
         HTTPStatus.FOUND),
        ('news:edit', pytest.lazy_fixture('author_client'),
         HTTPStatus.OK),
        ('news:edit', pytest.lazy_fixture('reader_client'),
         HTTPStatus.NOT_FOUND),
        ('news:delete', pytest.lazy_fixture('client'),
         HTTPStatus.FOUND),
        ('news:delete', pytest.lazy_fixture('author_client'),
         HTTPStatus.OK),
        ('news:delete', pytest.lazy_fixture('reader_client'),
         HTTPStatus.NOT_FOUND)
    ),
)
def test_edit_comment(parametrized_client, name, comment, expected_status):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, note_object',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment'))
    ),
)
def test_redirects(client, name, note_object):
    login_url = reverse('users:login')
    url = reverse(name, args=(note_object.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
