# IMEI-check бот и flask API

## Features

Проверка IMEI номера на валидность.

## Dependencies

[aiogram](https://github.com/aiogram/aiogram)
[python-dotenv](https://github.com/theskumar/python-dotenv)
[Flask](https://flask.palletsprojects.com/en/2.3.x/)

## Setup

Подготовьте виртуальное окружение и установите зависимости.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Создайте файл .env в директории bot и заполните по образцу в .env.sample.

## Running

Telegram-бот:

```bash
python -m bot.main
```

Flask API:

```bash
flask --app bot.api.flask_app run
```
