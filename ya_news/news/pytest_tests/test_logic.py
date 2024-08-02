import pytest
from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from news.models import Comment, News
from news.forms import BAD_WORDS, WARNING

User = get_user_model()

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client):
    """Анонимный пользователь не может отправить комментарий."""
    news = News.objects.create(title='Заголовок', text='Текст')
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


# могу эти два теста объединить в один
def test_user_can_create_comment(author_client):
    """Авторизованный пользователь может отправить комментарий."""
    news = News.objects.create(title='Заголовок', text='Текст')
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}
    author_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_user_cant_use_bad_words(author_client, news):
    """Комментарий с запрещённым словом не будет опубликован, а форма
    вернёт ошибку.
    """
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assert response.context['form'].errors['text'] == [WARNING]
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_delete_comment(not_author_client, author_client,
                        comment):  # Решил разбить и объединить тесты
    """Авторизованный пользователь может удалять свои комментарии.
    Авторизованный пользователь не может удалять чужие комментарии.
    """
    # Адрес удаления комментария
    delete_url = reverse('news:delete', args=(comment.id, ))
    # Попытка удалить чужой комментарий
    response = not_author_client.delete(delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    comments_count = Comment.objects.count()
    assert comments_count == 1
    # Попытка удалить свой комментарий
    response = author_client.delete(delete_url)
    # Убедимся, что комментарий удалён.
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_edit_comment(not_author_client, author_client, comment):
    """Авторизованный пользователь может редактировать свои комментарии.
    Авторизованный пользователь не может редактировать чужие комментарии.
    """
    # Адрес изменения комментария.
    edit_url = reverse('news:edit', args=(comment.id, ))
    # Делаем запрос редактирования чужого комментария.
    response = not_author_client.post(edit_url, data={'text': NEW_COMMENT})
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == COMMENT_TEXT
    # Делаем запрос редактирования своего комментария.
    response = author_client.post(edit_url, data={'text': NEW_COMMENT})
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст изменился
    assert comment.text == NEW_COMMENT
