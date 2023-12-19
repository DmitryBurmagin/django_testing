from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.edit_url = reverse('notes:edit', kwargs={'slug': 'note'})
        cls.del_url = reverse('notes:delete', kwargs={'slug': 'note'})
        cls.note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'note',
        }

    def test_auth_create_note(self):
        initial_note_count = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.note_data)
        self.assertRedirects(response, self.success_url)
        final_note_count = Note.objects.count()
        self.assertEqual(final_note_count, initial_note_count + 1)
        note = Note.objects.latest('id')
        self.assertEqual(note.title, self.note_data['title'])
        self.assertEqual(note.text, self.note_data['text'])
        self.assertEqual(note.slug, self.note_data['slug'])

    def test_anonymous_create_note(self):
        anonymous_client = Client()
        response = anonymous_client.post(self.add_url, data=self.note_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_create_duplicate_slug(self):
        for cnt in range(2):
            response = self.author_client.post(
                self.add_url,
                data=self.note_data
            )
            if response.status_code == HTTPStatus.FOUND:
                self.assertRedirects(response, self.success_url)
            else:
                self.assertEqual(response.status_code, HTTPStatus.OK)
                note_count = Note.objects.count()
                self.assertEqual(note_count, cnt)
                self.assertFormError(
                    response,
                    'form',
                    'slug',
                    self.note_data['slug'] + WARNING
                )

    def test_create_note_no_slug(self):
        del self.note_data['slug']
        response = self.author_client.post(self.add_url, data=self.note_data)
        self.assertRedirects(response, self.success_url)
        note = Note.objects.last()
        create_slug = slugify(self.note_data['title'])
        self.assertNotEqual(note.slug, create_slug)

    def test_edit_note_auth_user(self):
        response = self.author_client.post(self.add_url, data=self.note_data)
        self.assertRedirects(response, self.success_url)

        # Запрос от читателя
        response = self.reader_client.post(self.edit_url, data=self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        # Запрос от автора
        response = self.author_client.post(self.edit_url, data=self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note = Note.objects.get(slug=self.note_data['slug'])
        self.assertEqual(note.title, self.note_data['title'])
        self.assertEqual(note.text, self.note_data['text'])

    def test_delete_note_auth_user(self):
        response = self.author_client.post(self.add_url, data=self.note_data)
        self.assertRedirects(response, self.success_url)

        # Запрос от читателя
        response = self.reader_client.delete(self.del_url, data=self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        # Запрос от автора
        response = self.author_client.delete(self.del_url, data=self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)
