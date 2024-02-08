import asyncio
import logging
import requests
import json

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
# from aiogram.fsm.storage.redis import RedisStorage




# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="6906727176:AAGXaFq5xWf_WgTKG90OvBMZgNMXbvsCWZY")
# Диспетчер
# redis_client = Redis.from_url("redis://localhost:6379")
# dp = Dispatcher(storage=RedisStorage(redis=redis_client))
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    url     = 'https://dnevnik2.petersburgedu.ru/api/user/auth/login'
    headers = { 'Content-Type' : 'application/json' }
    payload =  { "type": "email", "login": "orezvova@gmail.com", "activation_code": "null", "password": "Ss37aMUb" }
    res = requests.post(url, data=json.dumps(payload), headers=headers)
    response_dict = json.loads(res.text)
    token_jwt = response_dict['data']['token']

    token = { 'X-Jwt-Token' : token_jwt}
    url_l = 'https://dnevnik2.petersburgedu.ru/api/journal/lesson/list-by-education?p_datetime_from=05.02.2024%2000:00:00&p_datetime_to=05.02.2024%2023:59:59&p_educations%5B%5D=908910'
    response = requests.post(url_l, data={}, headers=token)
    response = json.loads(response.text)

    nl = '\n'
    for i in response['data']['items']:
        if i["tasks"]:
            await message.answer(f'Предмет: {i["subject_name"]}{nl}Домашнее задание: {i["tasks"][0]["task_name"]}{nl}')
        else:
            await message.answer(f'Предмет: {i["subject_name"]}{nl}Домашнего задания нет (¬‿¬ ){nl}')


@dp.message(Command("reg"))
async def cmd_start(message: types.Message):
    await message.answer(f'введите логин')


    # print(response['data']['items'])

    # await message.answer("hello")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
