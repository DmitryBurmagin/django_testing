from datetime import datetime, timedelta

import pytest
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
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


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
    News.objects.bulk_create([
        News(title=f'Новость {i}') for i in range(11)
    ])


@pytest.fixture
def create_comment(author, comment):
    news = News.objects.create(
        title='Тестовая новость'
    )
    detail_url = reverse('news:detail', args=(news.pk,))
    now = datetime.now()
    for i in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {i}',
        )
        comment.created = (now + timedelta(days=i)).astimezone(timezone.utc)
        comment.save()
    return news, detail_url, comment


@pytest.fixture
def form_data(author, news):
    return {
        'news': news.pk,
        'text': 'Новый текст',
        'author': author,
        'created': datetime.now()
    }
