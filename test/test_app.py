import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_add(client):
    response = client.get('/add?a=5&b=3')
    assert response.status_code == 200
    assert response.get_json() == {'result': 8.0}

def test_subtract(client):
    response = client.get('/subtract?a=10&b=4')
    assert response.status_code == 200
    assert response.get_json() == {'result': 6.0}

def test_multiply(client):
    response = client.get('/multiply?a=7&b=6')
    assert response.status_code == 200
    assert response.get_json() == {'result': 42.0}

def test_divide(client):
    response = client.get('/divide?a=20&b=5')
    assert response.status_code == 200
    assert response.get_json() == {'result': 4.0}

def test_divide_by_zero(client):
    response = client.get('/divide?a=10&b=0')
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Division by zero'}

def test_3wina(client):
    response = client.get('/3wina')
    assert response.status_code == 200
    assert response.get_json() == "i see you !"
