import asyncio
import logging
import requests
import json


from aiogram import Bot, Dispatcher, types, F, Router, html
from typing import Any, Dict
from datetime import datetime
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

form_router = Router()


class Form(StatesGroup):
    login = State()
    password = State()
    user_id = State()



# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="6906727176:AAGXaFq5xWf_WgTKG90OvBMZgNMXbvsCWZY")
# Диспетчер
# redis_client = Redis.from_url("redis://localhost:6379")
# dp = Dispatcher(storage=RedisStorage(redis=redis_client))
dp = Dispatcher()


    

# Хэндлер на команду /start
@dp.message(Command("lessons"))
async def cmd_start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    login = data["login"]
    password = data["password"]
    url     = 'https://dnevnik2.petersburgedu.ru/api/user/auth/login'
    headers = { 'Content-Type' : 'application/json' }
    payload =  { "type": "email", "login": login, "activation_code": "null", "password": password }
    res = requests.post(url, data=json.dumps(payload), headers=headers)
    response_dict = json.loads(res.text)
    token_jwt = response_dict['data']['token']

    token = { 'X-Jwt-Token' : token_jwt}
    today = datetime.today()
    datem = today.strftime("%d.%m")
    url_l = f'https://dnevnik2.petersburgedu.ru/api/journal/lesson/list-by-education?p_datetime_from={datem}.2024%2000:00:00&p_datetime_to={datem}.2024%2023:59:59&p_educations%5B%5D=908910'
    response = requests.post(url_l, data={}, headers=token)
    response = json.loads(response.text)

    nl = '\n'
    for i in response['data']['items']:
        if i["tasks"]:
            await message.answer(f'Предмет: {i["subject_name"]}{nl}Домашнее задание: {i["tasks"][0]["task_name"]}{nl}')
        else:
            await message.answer(f'Предмет: {i["subject_name"]}{nl}Домашнего задания нет (¬‿¬ ){nl}')


@dp.message(Command("reg"))
async def login_step(message: types.Message, state: FSMContext):
    await message.answer(text='Привет! Напиши свой логин(email) без лишних пробелов:')
    await state.set_state(Form.login)


@dp.message(Form.login)
async def password_step(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(Form.password)
    await state.update_data(name_user=message.text.title())
    await message.answer(text='Твой пароль:')


@dp.message(Form.password)
async def send_step(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await cmd_start(message=message, state=state)

# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_router(form_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
