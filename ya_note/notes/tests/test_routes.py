from django.contrib.auth import get_user_model

from .conftest import BaseClass

User = get_user_model()


class TestRoutes(BaseClass):

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

        address_forwarding = [
            # Проверка переадресации на страницу логина
            [self.url_delete, self.delete_url_redirect],
            [self.url_edit, self.edit_url_redirect],
        ]
        for page, expected_url in address_forwarding:
            response = self.client.get(page)
            self.assertRedirects(response, expected_url)
