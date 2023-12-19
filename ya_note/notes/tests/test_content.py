from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    LIST_NOTE = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель автора')
        cls.auth_client = Client()
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='note',
            author=cls.author
        )
        cls.auth_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_context_list(self):
        users_notes = (
            (self.auth_client, self.author, True),
            (self.reader_client, self.reader, False),
        )
        url = reverse('notes:list')
        for client, user, note_in_list in users_notes:
            with self.subTest(user=user, note_in_list=note_in_list):
                response = client.get(url)
                note_in_object_list = self.note in response.context[
                    'object_list']
                self.assertEqual(note_in_object_list, note_in_list)

    def test_auth_user_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
