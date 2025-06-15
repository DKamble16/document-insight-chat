from rag.test.fixtures import database


db = database()

def test_get_messages(rest):
    response = rest.get('/ping')
    assert response.data == {'data': 'pong!'}
