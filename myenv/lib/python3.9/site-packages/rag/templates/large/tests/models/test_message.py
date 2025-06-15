import pytest
from rag.test.fixtures import database
from api.models import Message


db = database()

@pytest.fixture(autouse=True, scope='function')
def message(db):
    return Message.objects.create()


def test_create_message():
    Message.objects.create()
    assert Message.objects.count() == 2

def test_delete_message(message):
    message.delete()
    assert Message.objects.count() == 0
