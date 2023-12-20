from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель автора')
        title = 'Заголовок'
        cls.note = Note.objects.create(
            title=title,
            text='Текст',
            slug=slugify(title),
            author=cls.author
        )
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_public_page(self):
        urls = (
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
            ('notes:home'),
        )
        for name in urls:
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_page(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            if user is None:
                urls = (
                    ('notes:add'),
                    ('notes:list'),
                    ('notes:success'),
                )
                for name in urls:
                    with self.subTest(name=name):
                        url = reverse(name)
                        response = self.client.get(url)
                        self.assertEqual(response.status_code, status)

    def test_edit_page(self):
        users_statuses = (
            (self.author, HTTPStatus.OK, self.author_client),
            (self.reader, HTTPStatus.NOT_FOUND, self.reader_client),
        )
        for user, status, client in users_statuses:
            urls = (
                ('notes:detail', (self.note.slug,)),
                ('notes:edit', (self.note.slug,)),
                ('notes:delete', (self.note.slug,))
            )
            for name, args in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=args)
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonymous(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:add'),
            ('notes:list'),
            ('notes:success'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
