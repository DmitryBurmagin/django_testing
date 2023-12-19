from datetime import datetime, timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст Новости',
        date=datetime.today()
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Это комментарий'
    )
    return comment


@pytest.fixture
def create_news(author, news):
    now = datetime.now()
    news_object = News.objects.bulk_create([
        News(
            title=f'Новость {i}',
            date=(now + timedelta(days=i)).astimezone(timezone.utc))
        for i in range(11)
    ])
    return news_object


@pytest.fixture
def create_comment(author, news, detail_url, comment):
    now = datetime.now()
    for i in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {i}',
        )
        comment.created = (now + timedelta(days=i)).astimezone(timezone.utc)
        comment.save()
