from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.conftest import BaseClass

User = get_user_model()


class TestHomePage(BaseClass):

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
