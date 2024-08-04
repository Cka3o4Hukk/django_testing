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
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author = User.objects.create(username='Владелец аккаунта')
        cls.reader = User.objects.create(username='Посторонний пользователь')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.author)
        cls.url_add = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.url_delete = reverse('notes:delete',
                                 kwargs={'slug': cls.note.slug})
        cls.url_detail = reverse('notes:detail',
                                 kwargs={'slug': cls.note.slug})
        cls.url_list = reverse('notes:list')
        cls.url_success = reverse('notes:success')
        cls.url_home = reverse('notes:home')
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_signup = reverse('users:signup')
        cls.http_ok = HTTPStatus.OK
        cls.http_not_found = HTTPStatus.NOT_FOUND
        cls.http_found = HTTPStatus.FOUND

    def test_pages_availability(self):
        cases = [
            # Главная, регистрация, вход, выход доступны всем пользователям.
            [self.url_home, self.client, self.http_ok],
            [self.url_login, self.client, self.http_ok],
            [self.url_logout, self.client, self.http_ok],
            [self.url_signup, self.client, self.http_ok],
            # При попытке перейти на страницу списка заметок, страницу
            # успешного добавления записи, страницу добавления заметки,
            # отдельной заметки, редактирования или удаления заметки анонимный
            # пользователь перенаправляется на страницу логина.
            [self.url_edit, self.client, self.http_found],
            [self.url_delete, self.client, self.http_found],
            [self.url_detail, self.client, self.http_found],
            # Аутентифицированному пользователю доступна страница со списком
            # заметок, страница успешного добавления заметки, страница
            # добавления новой заметки add/.
            [self.url_list, self.author_client, self.http_ok],
            [self.url_success, self.author_client, self.http_ok],
            [self.url_add, self.author_client, self.http_ok],
        ]
        for page, user, status_code in cases:
            response = user.get(page)
            self.assertEqual(response.status_code, status_code)
