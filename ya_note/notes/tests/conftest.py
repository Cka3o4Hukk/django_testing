from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Базовый метод."""
        cls.author = User.objects.create(username='Комментатор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
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
        cls.delete_url_redirect = f'{cls.url_login}?next={cls.url_delete}'
        cls.edit_url_redirect = f'{cls.url_login}?next={cls.url_edit}'
