import datetime

from flask import Flask, request, jsonify

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from backend.database.orm import DatabaseManager, Train, Car, Cart, Axle


app = Flask(__name__)


Session = sessionmaker(bind=DatabaseManager.sync_engine)
session = Session()


@app.route('/trains', methods=['POST'])
def create_train():
    try:
        data = request.json
        dt = datetime.datetime.fromisoformat(data['datetime'])
        train = Train(datetime=dt, direction=data['direction'])
        session.add(train)
        session.commit()
        return jsonify({'message': 'Train created', 'train': train.to_dict()}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/trains', methods=['GET'])
def get_trains():
    try:
        trains = session.query(Train).all()
        return jsonify([train.to_dict() for train in trains]), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/trains/<int:train_id>', methods=['DELETE'])
def delete_train(train_id):
    try:
        train = session.get(Train, train_id)
        if not train:
            return jsonify({'error': 'Train not found'}), 404
        session.delete(train)
        session.commit()
        return jsonify({'message': 'Train deleted'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/cars', methods=['POST'])
def add_car():
    try:
        data = request.json
        car = Car(train_id=data['train_id'], weight=0)
        session.add(car)
        session.commit()
        return jsonify({'message': 'Car added', 'car': car.to_dict()}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/cars/<int:car_id>/calculate_weight', methods=['GET'])
def calculate_car_weight(car_id):
    try:
        car = session.get(Car, car_id)
        if not car:
            return jsonify({'error': 'Car not found'}), 404

        total_weight = sum(
            axle.weight for cart in car.carts for axle in cart.axles)
        car.weight = total_weight
        session.commit()

        return jsonify({'car_id': car_id, 'total_weight': total_weight}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/carts', methods=['POST'])
def add_cart():
    try:
        data = request.json
        cart = Cart(car_id=data['car_id'])
        session.add(cart)
        session.commit()
        return jsonify({'message': 'Cart added', 'cart_id': cart.id}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/axles', methods=['POST'])
def add_axle():
    try:
        data = request.json
        axle = Axle(cart_id=data['cart_id'],
                    weight=data['weight'], speed=data['speed'])
        session.add(axle)
        session.commit()
        return jsonify({'message': 'Axle added', 'axle_id': axle.id}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@app.route('/axles/<int:axle_id>', methods=['DELETE'])
def delete_axle(axle_id):
    try:
        axle = session.get(Axle, axle_id)
        if not axle:
            return jsonify({'error': 'Axle not found'}), 404
        session.delete(axle)
        session.commit()
        return jsonify({'message': 'Axle deleted'}), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
