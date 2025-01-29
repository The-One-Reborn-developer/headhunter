import os

from flask import Flask, request, current_app, jsonify

from dotenv import find_dotenv, load_dotenv

from bot.api_provider.requests import get_imei_info

app = Flask(
    __name__
)
load_dotenv(find_dotenv())


@app.post('/api/check-imei')
def check_imei_handler():
    try:
        data = request.get_json()
        imei_number = data.get('imei')
        token = data.get('token')

        if token != os.getenv('API_SANDBOX') or token != os.getenv('API_LIVE'):
            return "403", 403

        response = get_imei_info(imei_number)
        return jsonify(response)
    except Exception as e:
        current_app.logger.error(f"Exception in check_imei_handler: {e}")
        return "500", 500


if __name__ == "__main__":
    app.run(debug=True)
