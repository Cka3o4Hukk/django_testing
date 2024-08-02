from datetime import datetime, timedelta
import pytest

from django.contrib.auth import get_user_model
from django.test.client import Client
from django.utils import timezone
from datetime import timedelta
from news.models import Comment, News

User = get_user_model()


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект заметки
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(  # Создаём комментарий
        text='Текст комментария',
        author=author,
        news=news,
    )
    return comment


@pytest.fixture
def list_news():
    all_news = []
    for index in range(11):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index))
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def create_comments(client, news, author):
    """Сортировка комментариев от старых к новым."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=News.objects.create
            (title='Тестовая новость', text='Просто текст.'),
            author=author,
            text=f'Tекст{index}')
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        #  И сохраняем эти изменения.
        comment.save()
