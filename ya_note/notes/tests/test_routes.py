from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.test import Client, TestCase

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Базовый метод."""
        cls.author = User.objects.create(username='Комментатор')
        cls.author_client = Client()
        cls.author_client .force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author = User.objects.create(username='Владелец аккаунта')
        cls.reader = User.objects.create(username='Посторонний пользователь')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.author)

    def test_pages_availability(self):
        """Главная страница, страницы регистрации пользователей, входа в
        учётную запись и выхода из неё доступны всем пользователям.
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """При попытке перейти на страницу списка заметок, страницу успешного
        добавления записи, страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None)
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                if args is not None:
                    url = reverse(name, args=args)
                else:
                    url = reverse(name)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url, args=None)
                # Ожидаем, что со всех проверяемых страниц анонимный клиент
                # будет перенаправлен на страницу логина:
                self.assertRedirects(response, expected_url)

    def test_availability_for_note_edit_and_delete(self):
        """Страницы отдельной заметки, редактирования и удаления заметки
        доступны только автору заметки. Если на эти страницы попытается зайти
        другой пользователь — вернётся ошибка 404.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability_for_auth_user(self):
        """Аутентифицированному пользователю доступна страница со списком
        заметок notes/, страница успешного добавления заметки done/, страница
        добавления новой заметки add/.
        """
        for name in ('notes:list', 'notes:success', 'notes:add'):
            url = reverse(name)
            response = self.author_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
