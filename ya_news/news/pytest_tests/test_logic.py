import pytest
from random import choice
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

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
    reader_client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.last()
    assert new_comment.news.pk == news.pk
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == reader


def test_user_cant_use_bad_words(reader_client, news):
    bad_words_data = {
        'text': f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'
    }
    url = reverse('news:detail', args=(news.id,))
    response = reader_client.post(url, data=bad_words_data)
    assert Comment.objects.count() == 0
    assertFormError(response, 'form', 'text', WARNING)


def test_auth_user_edit_comments(author_client, author, news, detail_url,
                                 comment):
    assert Comment.objects.filter(pk=comment.pk).exists()
    url = reverse('news:edit', args=(comment.pk,))
    response = author_client.post(url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{detail_url}#comments'
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_auth_user_delete_comments(author_client, detail_url, comment):
    assert Comment.objects.filter(pk=comment.pk).exists()
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{detail_url}#comments'
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_anonymous_user_not_edit_comments(client, name, comment):
    login_url = reverse('users:login')
    assert Comment.objects.filter(pk=comment.pk).exists()
    url = reverse(name, args=(comment.pk,))
    response = client.post(url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{login_url}?next={url}'
