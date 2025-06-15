import pytest
from rag.test.fixtures import rest, database
from api.models import Message, User


# fixtures
db = database(transactional=True)

@pytest.fixture()
def user(db):
    user = User(username='example')
    user.save()
    return user

@pytest.fixture()
def message(db, user):
    return Message.create(text='Hello world!', user=user)


# tests
def test_create_message(rest, user):
    response = rest.post('/messages', {'text': 'hello', 'user': user.id})
    assert Message.objects.count() == 1
    assert response.data['text'] == 'hello'

    response = rest.post('/messages', {'bogus': 'data'})
    assert response.status == 400

def test_get_message(rest, message):
    response = rest.get(f'/messages/{message.id}')
    assert response.data['text'] == message.text

    response = rest.get(f'/messages/321')
    assert response.status == 404

def test_get_messages(rest, message):
    response = rest.get(f'/messages')
    assert str(message.id) in response.data
    assert len(response.data) == 1

def test_update_message(rest, message):
    response = rest.put(f'/messages/{message.id}', {'text': 'hello'})
    assert Message.objects.count() == 1
    assert response.data['text'] == 'hello'

    response = rest.put(f'/messages/{message.id}', {'bogus': 'data'})
    assert response.status == 400

    response = rest.put(f'/messages/321', {'text': 'hello'})
    assert response.status == 404

def test_delete_message(rest, message):
    response = rest.delete(f'/messages/{message.id}')
    assert response.data['text'] == message.text
    assert Message.objects.count() == 0

    response = rest.delete(f'/messages/321')
    assert response.status == 404
