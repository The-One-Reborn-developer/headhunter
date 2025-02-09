import logging

from app.api.flask_app import app


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)

    app.run(debug=True)
