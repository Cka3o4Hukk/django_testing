from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

HOME_URL = 'news:home'
DETAIL_URL = 'news:detail'


def test_pages_contains_form(author_client, comment):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    # Формируем URL.
    url = reverse(DETAIL_URL, args=(comment.id, ))
    # Запрашиваем нужную страницу:
    response = author_client.get(url)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], CommentForm)


def test_page_of_missing_form(client, comment):
    """Анонимному  пользователю недоступна форма для отправки комментария."""
    # Формируем URL.
    url = reverse(DETAIL_URL, args=(comment.id, ))
    # Запрашиваем нужную страницу:
    response = client.get(url)
    # Проверяем, что объекта формы нет в классе.
    assert 'form' not in response.context


def test_page_of_missing_form(author_client, comment, list_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse(HOME_URL)
    response = author_client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(author_client, comment, list_news):
    """Сортировка новостей от новых к старым."""
    url = reverse(HOME_URL)
    response = author_client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(author_client, news, author):
    """Сортировка комментариев от старых к новым."""
    url = reverse(DETAIL_URL, args=(news.id,))
    response = author_client.get(url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    # Проверяем, что временные метки отсортированы правильно.
    assert all_timestamps == sorted_timestamps


def test_authorized_client_has_form(author_client, client, news):
    """Проверка доступа к форме для отправки комментария."""
    url = reverse(DETAIL_URL, args=(news.id,))
    if client:
        response = client.get(url)
        assert 'form' not in response.context
    response = author_client.get(url)
    assert 'form' in response.context
