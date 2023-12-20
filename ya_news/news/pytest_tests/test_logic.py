from random import choice
from http import HTTPStatus as SCode

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from pytest_lazyfixture import lazy_fixture as lf

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA = {
    'text': 'Новый текст'
}


@pytest.mark.django_db
def test_anonymous_user_not_create_comment(client, detail_url):
    initial_comment_count = Comment.objects.count()
    response = client.post(detail_url, data=FORM_DATA)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == initial_comment_count


def test_auth_user_create_comment(reader_client, reader, detail_url, news):
    initial_comment_count = Comment.objects.count()
    reader_client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == initial_comment_count + 1
    new_comment = Comment.objects.last()
    assert new_comment.news.pk == news.pk
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == reader


def test_user_cant_use_bad_words(reader_client, detail_url):
    initial_comment_count = Comment.objects.count()
    bad_words_data = {
        'text': f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'
    }
    response = reader_client.post(detail_url, data=bad_words_data)
    assert Comment.objects.count() == initial_comment_count
    assertFormError(response, 'form', 'text', WARNING)


def test_auth_user_edit_comments(author_client, author, news, edit_url,
                                 detail_url, comment):
    assert Comment.objects.filter(pk=comment.pk).exists()
    response = author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == SCode.FOUND
    assert response.url == f'{detail_url}#comments'
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_auth_user_delete_comments(author_client, detail_url, del_url,
                                   comment):
    assert Comment.objects.filter(pk=comment.pk).exists()
    response = author_client.post(del_url)
    assert response.status_code == SCode.FOUND
    assert response.url == f'{detail_url}#comments'
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.parametrize(
    'name',
    (lf('edit_url'), lf('del_url'))
)
def test_anonymous_user_not_edit_comments(client, name, comment):
    login_url = reverse('users:login')
    assert Comment.objects.filter(pk=comment.pk).exists()
    response = client.post(name, data=FORM_DATA)
    assert response.status_code == SCode.FOUND
    assert response.url == f'{login_url}?next={name}'
