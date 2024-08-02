from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Базовый метод."""
        cls.user = User.objects.create(username='Владелец аккаунта')
        cls.reader = User.objects.create(username='Посторонний пользователь')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.user, slug='123')

    def test_pages_availability(self):
        """Тест страниц для неавторизованного пользователя."""
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
        """Тест переадресации на страницу входа неавторизованных"""
        """пользователей."""  # flake 8 ругает, тк не вмещается в 1 строку
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_edit_and_delete(self):
        """Тест на страницу входа."""
        users_statuses = (
            (self.user, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
