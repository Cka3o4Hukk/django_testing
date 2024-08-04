import pytest
from http import HTTPStatus
from django.contrib.auth import get_user_model
from news.models import Comment
from news.forms import BAD_WORDS, WARNING

User = get_user_model()

NEW_COMMENT = 'Обновлённый комментарий'
FORM_DATA = {'text': 'Текст комментария'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, url_detail):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(url_detail, data=FORM_DATA)
    comments_count = Comment.objects.count()
    assert comments_count == 0


# могу эти два теста объединить в один
def test_user_can_create_comment(author_client, news, url_detail):
    """Авторизованный пользователь может отправить комментарий."""
    author_client.post(url_detail, data=FORM_DATA)
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news, bad_word, url_detail):
    """Комментарий с запрещённым словом не будет опубликован, а форма
    вернёт ошибку.
    """
    # Неуверен, что это верно
    #  for bad_word in BAD_WORDS:
    #    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}

    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(url_detail, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assert response.context['form'].errors['text'] == [WARNING]
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_delete_comment(not_author_client, author_client, url_delete,
                        comment):
    """Авторизованный пользователь может удалять свои комментарии.
    Авторизованный пользователь не может удалять чужие комментарии.
    """
    # Попытка удалить чужой комментарий
    response = not_author_client.delete(url_delete)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    comments_count = Comment.objects.count()
    assert comments_count == 1
    # Попытка удалить свой комментарий
    response = author_client.delete(url_delete)
    # Убедимся, что комментарий удалён.
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_edit_comment(not_author_client, author_client, comment, url_edit):
    """Авторизованный пользователь может редактировать свои комментарии.
    Авторизованный пользователь не может редактировать чужие комментарии.
    """
    # Адрес изменения комментария.
    # Делаем запрос редактирования чужого комментария.
    response = not_author_client.post(url_edit, data={'text': NEW_COMMENT})
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == FORM_DATA['text']
    # Делаем запрос редактирования своего комментария.
    response = author_client.post(url_edit, data={'text': NEW_COMMENT})
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст изменился
    assert comment.text == NEW_COMMENT
