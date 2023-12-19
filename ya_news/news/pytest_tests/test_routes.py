from http import HTTPStatus as SCode

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_home_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == SCode.OK


def test_news_detail_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == SCode.OK


@pytest.mark.parametrize(
    'name, parametrized_client, expected_status, expected_redirect',
    (
        (lf('edit_url'), lf('client'), SCode.FOUND, True),
        (lf('edit_url'), lf('author_client'), SCode.OK, False),
        (lf('edit_url'), lf('reader_client'), SCode.NOT_FOUND, False),
        (lf('del_url'), lf('client'), SCode.FOUND, True),
        (lf('del_url'), lf('author_client'), SCode.OK, False),
        (lf('del_url'), lf('reader_client'), SCode.NOT_FOUND, False)
    ),
)
def test_edit_comment(parametrized_client, name, expected_status,
                      expected_redirect):
    response = parametrized_client.get(name)
    assert response.status_code == expected_status
    if expected_redirect:
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={name}'
        assertRedirects(response, expected_url)
