import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING, CommentForm
from news.models import Comment
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_anonymous_user_not_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_auth_user_create_comment(reader_client, reader, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    reader_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news.pk == news.pk
    assert new_comment.text == 'Новый текст'
    assert new_comment.author == reader


def test_user_cant_use_bad_words(reader_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    reader_client.post(url, data=bad_words_data)
    form = CommentForm(data=bad_words_data)
    form.is_valid()
    assert Comment.objects.count() == 0
    assert form.errors['text'] == [WARNING]


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_auth_user_edit_comments(author_client, name, news, comment,
                                 form_data):
    assert Comment.objects.filter(pk=comment.pk).exists()
    url = reverse(name, args=(comment.pk,))
    response = author_client.post(url, data=form_data)
    assert response.status_code == 302
    assert response.url == f'/news/{news.pk}/#comments'
    if name == 'news:delete':
        assert not Comment.objects.filter(pk=comment.pk).exists()
    else:
        comment.refresh_from_db()
        assert comment.text == form_data['text']


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_anonymous_user_not_edit_comments(client, name, comment, form_data):
    login_url = reverse('users:login')
    assert Comment.objects.filter(pk=comment.pk).exists()
    url = reverse(name, args=(comment.pk,))
    response = client.post(url, data=form_data)
    assert response.status_code == 302
    assert response.url == f'{login_url}?next={url}'
