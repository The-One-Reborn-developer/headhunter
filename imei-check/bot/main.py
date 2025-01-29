import asyncio
import os
import logging

from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher

from bot.routes.start import start_router
from bot.database.orm import User, DatabaseManager


async def main() -> None:
    load_dotenv(find_dotenv())

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )
    logging.info('Initializing database...')
    DATABASE = DatabaseManager()
    logging.info('Creating tables...')
    DATABASE.create_tables()
    logging.info('Tables created.')

    logging.info('Starting bot.')
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    dp = Dispatcher()
    logging.info('Dispatcher created.')

    dp.include_router(start_router)
    logging.info('Routes added.')

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info('Webhook deleted.')
    logging.info('Starting polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
