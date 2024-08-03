from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestCommentCreation(TestCase):
    @staticmethod
    def form_data():
        """Форма заметки."""
        return {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    @classmethod
    def setUpTestData(cls):
        """Базовый метод."""
        cls.author = User.objects.create(username='Комментатор')
        cls.author_client = Client()
        cls.author_client .force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.url_add = reverse('notes:add')

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.author_client.post(self.url_add, data=self.form_data())
        # Проверяем, что мы перешли на страницу успешного добавления заметки.
        self.assertRedirects(response, reverse('notes:success'))
        # Считаем общее количество заметок в БД, ожидаем 1 заметку.
        assert Note.objects.count() == 1
        # Проверяем поля заметки
        new_note = Note.objects.get()
        # Сверяем атрибуты объекта с ожидаемыми.

        # Но если заметка добавлена успешно, надо ли проверять поля?
        assert new_note.title == self.form_data()['title']
        assert new_note.text == self.form_data()['text']
        assert new_note.slug == self.form_data()['slug']
        assert new_note.author == self.author

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        # Через анонимный клиент пытаемся создать заметку:
        response = self.client.post(self.url_add, data=self.form_data())
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url_add}'
        # Проверяем, что произошла переадресация на страницу логина:
        self.assertRedirects(response, expected_url)
        # Считаем количество заметок в БД, ожидаем 0 заметок.
        assert Note.objects.count() == 0

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        # Делаем запрос на создание заметки
        response = self.author_client.post(self.url_add, data=self.form_data())
        # Производим повторный запрос на создание заметки, данные те же
        response = self.author_client.post(self.url_add, data=self.form_data())
        # Проверяем, что в ответе содержится ошибка формы для поля slug:
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.form_data()['slug'] + WARNING))
        # Убеждаемся, что количество заметок в базе осталось равным 1.
        assert Note.objects.count() == 1

    def test_empty_slug(self):
        """Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        # Делаем запрос на создание заметки, slug указываем пустой
        response = self.author_client.post(
            self.url_add, data={**self.form_data(), 'slug': ''})
        # Проверяем, что даже без slug заметка была создана:
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        # Получаем созданную заметку из базы:
        new_note = Note.objects.get()
        # Формируем ожидаемый slug:
        expected_slug = slugify(self.form_data()['title'])
        # Проверяем, что slug заметки соответствует ожидаемому:
        assert new_note.slug == expected_slug

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        # note = Note.objects.create(slug='new-slug', author=self.author)
        # так работает, но заполню полностью
        # Создаю заметку вручную, так как нужно проверить новые данные из формы
        note = Note.objects.create(title='Заголовок', text='Текст',
                                   slug='slug', author=self.author)
        # Открываем страницу редактирования заметки
        self.url_edit = reverse('notes:edit', kwargs={'slug': 'slug'})
        # Отправляем form_data - новые значения для полей заметки.
        response = self.author_client.post(
            self.url_edit, data=self.form_data())
        # Проверяем редирект:
        self.assertRedirects(response, reverse('notes:success'))
        note.refresh_from_db()
        # Проверяем, что атрибуты заметки обновлены.
        assert note.title == self.form_data()['title']
        assert note.text == self.form_data()['text']
        assert note.slug == self.form_data()['slug']

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        # Создаём заметку
        response = self.author_client.post(self.url_add, data=self.form_data())
        self.assertRedirects(response, reverse('notes:success'))
        # Проверяем, что она появилась
        assert Note.objects.count() == 1
        # Отправляем запрос с удалением заметки
        self.url_delete = reverse(
            'notes:delete', kwargs={'slug': self.form_data()['slug']})
        self.author_client.post(self.url_delete)
        # Проверяем количество заметок, ожидаем 0.
        assert Note.objects.count() == 0

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        # Создаём заметку
        self.author_client.post(self.url_add, data=self.form_data())
        assert Note.objects.count() == 1
        # Отправляем запрос с удалением заметки
        self.url_delete = reverse(
            'notes:delete', kwargs={'slug': self.form_data()['slug']})
        self.reader_client.post(self.url_delete)
        # Проверяем наличие записи
        assert Note.objects.count() == 1
# мог бы объединить тесты, но решил не смешивать, дабы не усложнять структуру

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать чужие заметки."""
        # Создаём заметку
        self.author_client.post(self.url_add, data=self.form_data())
        assert Note.objects.count() == 1
        # Отправляем запрос на страницу редактирования
        # Отправляем form_data - новые значения для полей заметки.
        self.url_edit = reverse(
            'notes:edit', kwargs={'slug': self.form_data()['slug']})
        self.reader_client.post(self.url_edit)
        # Проверяем наличие записи
        assert Note.objects.count() == 1
