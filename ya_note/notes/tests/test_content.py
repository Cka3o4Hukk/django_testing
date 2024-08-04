from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Базовый метод."""
        cls.author = User.objects.create(username='Комментатор')
        cls.author_client = Client()
        cls.author_client .force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.author)
        cls.url_add = reverse('notes:add')
        cls.url_list = reverse('notes:list')
        cls.url_edit = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.http_ok = HTTPStatus.OK

    def test_create_note_page_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        pages = [self.url_add, self.url_edit]
        for page in pages:
            with self.subTest():
                response = self.author_client.get(page)
                self.assertEqual(response.status_code, self.http_ok)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_notes_list_for_different_users(self):
        """Отдельная заметка передаётся на страницу со списком заметок в списке
        object_list в словаре context. В список заметок одного пользователя не
        попадают заметки другого пользователя.
        """
        # Задаём названия для параметров.
        cases = [
            [self.author_client, True],
            [self.reader_client, False],
        ]
        for user, args in cases:
            response = user.get(self.url_list)
            # Проверяем истинность утверждения "заметка есть в списке":
            object_list = response.context['object_list']
            assert (self.note in object_list) is args
