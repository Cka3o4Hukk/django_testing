from django.conf import settings

from news.forms import CommentForm


def test_pages_contains_form(author_client, comment, url_detail):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    # Запрашиваем нужную страницу:
    response = author_client.get(url_detail)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], CommentForm)


def test_page_of_missing_form(client, comment, url_detail):
    """Анонимному  пользователю недоступна форма для отправки комментария."""
    # Запрашиваем нужную страницу:
    response = client.get(url_detail)
    # Проверяем, что объекта формы нет в классе.
    assert 'form' not in response


def test_page_of_missing_form(author_client, list_news, url_home):
    """Количество новостей на главной странице — не более 10."""
    response = author_client.get(url_home)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(author_client, list_news, url_home):
    """Сортировка новостей от новых к старым."""
    response = author_client.get(url_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(author_client, news, author, url_detail):
    """Сортировка комментариев от старых к новым."""
    response = author_client.get(url_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    # Проверяем, что временные метки отсортированы правильно.
    assert all_timestamps == sorted_timestamps


def test_authorized_client_has_form(author_client, client, news, url_detail):
    """Проверка доступа к форме для отправки комментария."""
    if client:
        response = client.get(url_detail)
        assert 'form' not in response.context
    response = author_client.get(url_detail)
    assert 'form' in response.context
