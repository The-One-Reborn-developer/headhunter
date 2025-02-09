from flask import Flask, request, jsonify

from app.database.orm import DatabaseManager, User, Account, Payment


app = Flask(__name__)


@app.post('/user/post')
def register_user():
    try:
        payload = request.json
        email = payload.get('email')
        password = payload.get('password')
        full_name = payload.get('full_name')
        is_admin = False  # Default

        if not email:
            return jsonify(result=False, message='Please provide email to register.')
        elif not password:
            return jsonify(result=False, message='Please provide password to register.')
        elif not full_name:
            return jsonify(result=False, message='Please provide your full name.')

        User.insert_entry(email=email, password=password,
                          full_name=full_name, is_admin=is_admin)

        return jsonify(result=True, message='User created.')
    except Exception as e:
        return jsonify(result=False, message='Unexpected server error.')


@app.get('/user/<email>')
def get_user(email):
    try:
        user = User.get_entry(email=email)

        return jsonify(result=True, data=user.to_dict())
    except Exception as e:
        return jsonify(result=False, message='Unexpected server error.')


@app.get('/user/<email>/account')
def get_account(email):
    try:
        user = User.get_entry(email=email)
        if not user:
            return jsonify(result=False, message='Error trying to fetch user`s account')

        account = Account.get_entry(user_id=user.id)
        if not account:
            return jsonify(result=False, message='Error trying to fetch user`s account')

        return jsonify(result=True, data=account.to_dict())
    except Exception as e:
        return jsonify(result=False, message='Unexpected server error.')


@app.get('/user/<email>/payments')
def get_payments(email):
    try:
        user = User.get_entry(email=email)
        if not user:
            return jsonify(result=False, message='Error trying to fetch user`s payments.')

        account = Account.get_entry(user_id=user.id)
        if not account:
            return jsonify(result=False, message='Error trying to fetch user`s payments')

        payments = Payment.get_entries(account_id=account.id)
        if not payments:
            return jsonify(result=False, message='Error trying to fetch user`s payments')

        return jsonify(result=True, data=[payment.to_dict() for payment in payments])
    except Exception as e:
        return jsonify(result=False, message='Unexpected server error.')
