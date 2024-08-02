from http import HTTPStatus
import pytest

from django.urls import reverse


@pytest.mark.parametrize(
    'name', ('users:login', 'users:logout', 'users:signup'))
def test_base_pages_availability_for_anonymous_user(client, name):
    """Главная страница доступна анонимному пользователю."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db  # Для анонимных пользователе нужна заглушка
@pytest.mark.parametrize(
    'name', ('news:detail', ))
def test_news_pages_availability_for_anonymous_user(news, client, name):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse(name, args=(news.id, ))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, news, expected_status, comment
):
    """Страницы удаления и редактирования коммента доступны только автору.
    Авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев (возвращается ошибка 404).
    """
    url = reverse(name, args=(comment.id, ))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:edit', 'news:delete'))
def test_edit(news, comment, author_client, name):
    """Страницы удаления и редактирования. коммента доступны только автору."""
    url = reverse(name, args=(comment.id, ))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:edit', 'news:delete'))
def test_transfer(news, comment, client, name):
    """При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации..
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id, ))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == expected_url
