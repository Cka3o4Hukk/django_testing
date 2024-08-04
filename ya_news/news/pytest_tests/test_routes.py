from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse_lazy


HOME_URL = pytest.lazy_fixture('url_home')
LOGIN_URL = pytest.lazy_fixture('url_login')
LOGOUT_URL = pytest.lazy_fixture('url_logout')
SIGNUP_URL = pytest.lazy_fixture('url_signup')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
DELETE_URL = pytest.lazy_fixture('url_delete')
EDIT_URL = pytest.lazy_fixture('url_edit')
DETAIL_URL = pytest.lazy_fixture('url_detail')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')
CLIENT = pytest.lazy_fixture('client')
HTTP_OK = HTTPStatus.OK
HTTP_FOUND = HTTPStatus.FOUND
HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND
URL = reverse_lazy('users:login')
DELETE_URL_REDIRECT = URL + f'?next={reverse_lazy("news:delete", args=(1, ))}'
EDIT_URL_REDIRECT = URL + f'?next={reverse_lazy("news:edit", args=(1, ))}'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, user, code',
    (
        (DELETE_URL, AUTHOR_CLIENT, HTTP_OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTP_OK),
        (DELETE_URL, NOT_AUTHOR_CLIENT, HTTP_NOT_FOUND),
        (EDIT_URL, NOT_AUTHOR_CLIENT, HTTP_NOT_FOUND),
        (DELETE_URL, CLIENT, HTTP_FOUND),
        (EDIT_URL, CLIENT, HTTP_FOUND),
        (DETAIL_URL, CLIENT, HTTP_OK),
        (HOME_URL, CLIENT, HTTP_OK),
        (LOGIN_URL, CLIENT, HTTP_OK),
        (LOGOUT_URL, CLIENT, HTTP_OK),
        (SIGNUP_URL, CLIENT, HTTP_OK)
    ),
)
def test_status_codes(
    url, user, code
):
    assert user.get(url).status_code == code


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, expected_url',
    (
        (DELETE_URL, DELETE_URL_REDIRECT),
        (EDIT_URL, EDIT_URL_REDIRECT),
    ),
)
def test_anonymous_redirects(client, url, expected_url):
    response = client.get(url)
    assertRedirects(response, expected_url)
