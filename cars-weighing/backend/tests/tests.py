import pytest

from backend.api.server import app, session
from backend.database.orm import Train, Car, Cart, Axle, DatabaseManager


@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    DatabaseManager.create_tables()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_and_teardown():
    session.begin_nested()
    session.query(Axle).delete()
    session.query(Cart).delete()
    session.query(Car).delete()
    session.query(Train).delete()
    session.commit()
    yield
    session.rollback()


def test_create_train(client):
    response = client.post('/trains', json={
        'datetime': '2025-02-05T12:00:00',
        'direction': 'North'
    })
    assert response.status_code == 201
    assert 'train' in response.json


def test_get_trains(client):
    client.post(
        '/trains', json={'datetime': '2025-02-05T12:00:00', 'direction': 'North'})
    response = client.get('/trains')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0


def test_delete_train(client):
    train_resp = client.post(
        '/trains', json={'datetime': '2025-02-05T12:00:00', 'direction': 'North'})
    train_id = train_resp.json['train']['id']
    response = client.delete(f'/trains/{train_id}')
    assert response.status_code == 200
    assert response.json['message'] == 'Train deleted'


def test_add_car(client):
    train_resp = client.post(
        '/trains', json={'datetime': '2025-02-05T12:00:00', 'direction': 'North'})
    train_id = train_resp.json['train']['id']

    response = client.post('/cars', json={'train_id': train_id})
    assert response.status_code == 201
    assert 'car' in response.json


def test_calculate_car_weight(client):
    train_resp = client.post(
        '/trains', json={'datetime': '2025-02-05T12:00:00', 'direction': 'North'})
    train_id = train_resp.json['train']['id']

    car_resp = client.post('/cars', json={'train_id': train_id})
    car_id = car_resp.json['car']['id']

    response = client.get(f'/cars/{car_id}/calculate_weight')
    assert response.status_code == 200
    assert 'total_weight' in response.json


def test_add_cart(client):
    train_resp = client.post(
        '/trains', json={'datetime': '2025-02-05T12:00:00', 'direction': 'North'})
    train_id = train_resp.json['train']['id']

    car_resp = client.post('/cars', json={'train_id': train_id})
    car_id = car_resp.json['car']['id']

    response = client.post('/carts', json={'car_id': car_id})
    assert response.status_code == 201
    assert 'cart_id' in response.json


def test_add_axle(client):
    train_resp = client.post(
        '/trains', json={'datetime': '2025-02-05T12:00:00', 'direction': 'North'})
    train_id = train_resp.json['train']['id']

    car_resp = client.post('/cars', json={'train_id': train_id})
    car_id = car_resp.json['car']['id']

    cart_resp = client.post('/carts', json={'car_id': car_id})
    cart_id = cart_resp.json['cart_id']

    response = client.post(
        '/axles', json={'cart_id': cart_id, 'weight': 1000.5, 'speed': 80})
    assert response.status_code == 201
    assert 'axle_id' in response.json


def test_delete_axle(client):
    train_resp = client.post(
        '/trains', json={'datetime': '2025-02-05T12:00:00', 'direction': 'North'})
    train_id = train_resp.json['train']['id']

    car_resp = client.post('/cars', json={'train_id': train_id})
    car_id = car_resp.json['car']['id']

    cart_resp = client.post('/carts', json={'car_id': car_id})
    cart_id = cart_resp.json['cart_id']

    axle_resp = client.post(
        '/axles', json={'cart_id': cart_id, 'weight': 1000.5, 'speed': 80})
    axle_id = axle_resp.json['axle_id']

    response = client.delete(f'/axles/{axle_id}')
    assert response.status_code == 200
    assert response.json['message'] == 'Axle deleted'
