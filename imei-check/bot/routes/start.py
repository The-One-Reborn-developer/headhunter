import os
import json

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.api_provider.requests import get_imei_info


class IMEICheck(StatesGroup):
    number = State()


PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(PROJECT_PATH, 'database')


start_router = Router()


@start_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    with open(os.path.join(DATABASE_PATH, 'whitelist.json'), 'r') as f:
        whitelist = json.load(f)

    if message.from_user.id not in whitelist['telegram_id']:
        await message.answer('Вы не находитесь в списке пользователей, которым разрешен доступ к боту.')
        return

    await state.set_state(IMEICheck.number)
    await message.answer('Введите IMEI-номер')


@start_router.message(IMEICheck.number)
async def number_handler(message: Message, state: FSMContext):
    imei_number = message.text

    if not imei_number.isdigit():
        await message.answer('IMEI-номер должен состоять только из цифр')
        return

    await message.answer('Проверяем IMEI-номер...')
    response = await get_imei_info(imei_number)

    await message.answer(response["message"])
    await state.clear()
