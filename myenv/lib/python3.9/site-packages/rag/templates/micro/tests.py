import pytest
from rag.test.fixtures import rest


# tests
def test_route_hello(rest):
    response = rest.get('/')
    assert response.data == {'data': 'hello world!'}

def test_route_echo(rest):
    response = rest.post('/echo', {'name': 'Liz'})
    assert response.data == {'name': 'Liz'}
