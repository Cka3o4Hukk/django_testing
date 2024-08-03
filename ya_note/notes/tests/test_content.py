from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


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
        # cls.note = Note.objects.create(author=cls.author) - работает
        # не понимаю как, но можно добавить заметку, указав лишь автора
        # скорее всего это будет ошибкой, поэтому я заполнил обязательные поля

    def test_create_note_page_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                # Передаём имя и позиционный аргумент в reverse()
                # и получаем адрес страницы для GET-запроса:
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_list_for_different_users(self):
        """Отдельная заметка передаётся на страницу со списком заметок в списке
        object_list в словаре context. В список заметок одного пользователя не
        попадают заметки другого пользователя.
        """
        # Задаём названия для параметров:
        users = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for name, args in users:
            with self.subTest(name=name):
                # Делаем запрос
                response = name.get(reverse('notes:list'))
                # Проверяем истинность утверждения "заметка есть в списке":
                object_list = response.context['object_list']
                assert (self.note in object_list) is args
