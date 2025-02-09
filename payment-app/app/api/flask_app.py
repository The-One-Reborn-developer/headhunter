import os
import logging

from flask import Flask, request, jsonify, current_app

from dotenv import load_dotenv, find_dotenv

from app.database.orm import User, Account, Payment
from app.utils.utils import verify_signature


find_dotenv(load_dotenv())


app = Flask(__name__)
app.config['PAYMENT_SECRET_KEY'] = os.getenv('PAYMENT_SECRET_KEY')


@app.post('/user/login')
def login_user():
    try:
        payload = request.json
        email = payload.get('email')
        password = payload.get('password')

        user = User.get_entry(email)
        if user.password != password:
            return jsonify(result=False, message='Wrong password.')
    except Exception as e:
        current_app.logger(e)
        return jsonify(result=False, message='Unexpected server error.')


@app.post('/user/register')
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
        current_app.logger(e)
        return jsonify(result=False, message='Unexpected server error.')


@app.get('/user/<email>')
def get_user(email):
    try:
        user = User.get_entry(email=email)

        return jsonify(result=True, data=user.to_dict())
    except Exception as e:
        current_app.logger(e)
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
        current_app.logger(e)
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
        current_app.logger(e)
        return jsonify(result=False, message='Unexpected server error.')


@app.post('/users/list')
def get_users():
    try:
        payload = request.json
        email = payload.get('email')

        is_admin = User.get_entry(email).is_admin
        if not is_admin:
            return jsonify(result=False, message='Not enough permissions.')

        users = User.get_entries()

        if not users:
            return jsonify(result=False, message='Failed to fetch users.')

        accounts = [user.accounts for user in users.to_dict()]
        return jsonify(result=True, data=accounts)
    except Exception as e:
        current_app.logger(e)
        return jsonify(result=False, message='Unexpected server error.')


@app.post('/payment')
def handle_payment():
    try:
        payload = request.json
        transaction_id = payload.get('transaction_id')
        account_id = payload.get('account_id')
        user_id = payload.get('user_id')
        amount = payload.get('amount')
        signature = payload.get('signature')

        if not all([transaction_id, account_id, user_id, amount, signature]):
            current_app.logger(
                f'Received data from webhook but the data is incomplete: {payload}')

        payload_string = (
            f'{account_id}{amount}{transaction_id}{user_id}{current_app.config['PAYMENT_SECRET_KEY']}')

        signature_verification = verify_signature(
            current_app.config['PAYMENT_SECRET_KEY'], signature, payload_string)
        if not signature_verification:
            current_app.logger(
                f'Received invalid transaction with wrong signature: {payload}')
    except Exception as e:
        current_app.logger(f'Error while processing payment from webhook: {e}')
