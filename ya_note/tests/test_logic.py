from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify
from notes.models import Note

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
        cls.note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'note',
        }

    def test_auth_create_note(self):
        response = self.author_client.post(self.add_url, data=self.note_data)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

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
            if response.status_code == 302:
                self.assertRedirects(response, self.success_url)
            else:
                self.assertEqual(response.status_code, 200)
                note_count = Note.objects.count()
                self.assertEqual(note_count, cnt)

    def test_create_note_no_slug(self):
        response = self.author_client.post(self.add_url, data=self.note_data)
        del self.note_data['slug']
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get(title='Новая заметка')
        create_slug = slugify(self.note_data['title'])
        self.assertNotEqual(note.slug, create_slug)

    def test_edit_note_auth_user(self):
        response = self.author_client.post(self.add_url, data=self.note_data)
        self.assertRedirects(response, self.success_url)
        edit_url = reverse('notes:edit', kwargs={'slug': 'note'})
        del_url = reverse('notes:delete', kwargs={'slug': 'note'})

        # Запрос читателя
        response = self.reader_client.post(edit_url, data=self.note_data)
        self.assertEqual(response.status_code, 404)

        # Запрос автора
        response = self.author_client.post(edit_url, data=self.note_data)
        self.assertEqual(response.status_code, 302)

        # Запрос на удаление от читателя
        response = self.reader_client.delete(del_url, data=self.note_data)
        self.assertEqual(response.status_code, 404)

        # Запрос на удаление от автора автора
        response = self.author_client.delete(del_url, data=self.note_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 0)
