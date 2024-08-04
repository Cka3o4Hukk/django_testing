from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestCommentCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Базовый метод."""
        cls.note = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.author = User.objects.create(username='Комментатор')
        cls.author_client = Client()
        cls.author_client .force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.url_add = reverse('notes:add')
        cls.url_login = reverse('users:login')
        cls.url_edit = reverse('notes:edit',
                               kwargs={'slug': cls.note['slug']})
        cls.url_delete = reverse('notes:delete',
                                 kwargs={'slug': cls.note['slug']})
        cls.url_success = reverse('notes:success')

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.author_client.post(self.url_add, data=self.note)
        self.assertRedirects(response, self.url_success)
        # Считаем общее количество заметок в БД, ожидаем 1 заметку.
        assert Note.objects.count() == 1
        # Проверяем поля заметки
        new_note = Note.objects.get()
        # Но если заметка добавлена успешно, надо ли проверять поля?
        assert new_note.title == self.note['title']
        assert new_note.text == self.note['text']
        assert new_note.slug == self.note['slug']
        assert new_note.author == self.author

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.client.post(self.url_add, data=self.note)
        expected_url = f'{self.url_login}?next={self.url_add}'
        # Проверяем, что произошла переадресация на страницу логина:
        self.assertRedirects(response, expected_url)
        # Считаем количество заметок в БД, ожидаем 0 заметок.
        assert Note.objects.count() == 0

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        response = self.author_client.post(self.url_add, data=self.note)
        # Производим повторный запрос на создание заметки, данные те же
        response = self.author_client.post(self.url_add, data=self.note)
        # Проверяем, что в ответе содержится ошибка формы для поля slug:
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note['slug'] + WARNING))
        # Убеждаемся, что количество заметок в базе осталось равным 1.
        assert Note.objects.count() == 1

    def test_empty_slug(self):
        """Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        response = self.author_client.post(
            self.url_add, data={**self.note, 'slug': ''})
        # Проверяем, что даже без slug заметка была создана:
        self.assertRedirects(response, self.url_success)
        assert Note.objects.count() == 1
        # Получаем созданную заметку из базы:
        new_note = Note.objects.get()
        # Формируем ожидаемый slug:
        expected_slug = slugify(self.note['title'])
        # Проверяем, что slug заметки соответствует ожидаемому:
        assert new_note.slug == expected_slug

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        note = Note.objects.create(title='Заголовок', text='Текст',
                                   slug='slug', author=self.author)
        # Вручную открываем страницу, так как нужен slug
        self.url_edit = reverse('notes:edit', kwargs={'slug': 'slug'})
        # Отправляем form_data - новые значения для полей заметки.
        response = self.author_client.post(
            self.url_edit, data=self.note)
        # Проверяем редирект:
        self.assertRedirects(response, self.url_success)
        note.refresh_from_db()
        # Проверяем, что атрибуты заметки обновлены.
        assert note.title == self.note['title']
        assert note.text == self.note['text']
        assert note.slug == self.note['slug']

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        response = self.author_client.post(self.url_add, data=self.note)
        self.assertRedirects(response, self.url_success)
        # Проверяем, что она появилась
        assert Note.objects.count() == 1
        # Отправляем запрос с удалением заметки
        self.author_client.post(self.url_delete)
        # Проверяем количество заметок, ожидаем 0.
        assert Note.objects.count() == 0

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        self.author_client.post(self.url_add, data=self.note)
        assert Note.objects.count() == 1
        # Отправляем запрос с удалением заметки
        self.reader_client.post(self.url_delete)
        # Проверяем наличие записи
        assert Note.objects.count() == 1

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.author_client.post(self.url_add, data=self.note)
        assert Note.objects.count() == 1
        # Отправляем запрос на страницу редактирования
        # Отправляем form_data - новые значения для полей заметки.
        self.reader_client.post(self.url_edit)
        # Проверяем наличие записи
        assert Note.objects.count() == 1
