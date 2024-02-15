import asyncio
import logging
import requests
import json


from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher, types, F, Router, html
from typing import Any, Dict
from datetime import datetime, timedelta
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
    person_id = State()
    jwt_token = State()



# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="6906727176:AAGXaFq5xWf_WgTKG90OvBMZgNMXbvsCWZY")
# Диспетчер
storage = RedisStorage.from_url("redis://localhost:6379")

dp = Dispatcher(storage=storage)
# dp = Dispatcher()

#@dp.message(Command("lessons"))

async def get_lessons(state: FSMContext):
    data = await state.get_data()
    person_id = data["person_id"]
    jwt_token = data["jwt_token"]
    today = datetime.now()
    if today.isoweekday() % 7 == 6:
        today = datetime.now() + timedelta(2)
    elif today.isoweekday() % 7 == 5:
        today = datetime.now() + timedelta(1)
        datem = today.strftime("%d.%m.%Y")
        url_l = f'https://dnevnik2.petersburgedu.ru/api/journal/schedule/list-by-education?p_page=1&p_datetime_from={datem}%2000:00:00&p_datetime_to={datem}%2023:59:59&p_educations%5B%5D={person_id}' 
        response = requests.post(url_l, data={}, headers=jwt_token)
        response = json.loads(response.text)
        if len(response['data']['items']) == 0:
            today = datetime.now() + timedelta(3)
        else:
            today = datetime.now() + timedelta(1)           
    else:
        today = datetime.now() + timedelta(1)
    
    datem = today.strftime("%d.%m.%Y")
    url_l = f'https://dnevnik2.petersburgedu.ru/api/journal/schedule/list-by-education?p_page=1&p_datetime_from={datem}%2000:00:00&p_datetime_to={datem}%2023:59:59&p_educations%5B%5D={person_id}' 
    response = requests.post(url_l, data={}, headers=jwt_token)
    response = json.loads(response.text)

    subject_names = list(set([x['subject_name'] for x in response['data']['items']]))
    Tasks = dict.fromkeys(subject_names,[])

    for i in range(9):
        today = datetime.now() - timedelta(i)
        datem = today.strftime("%d.%m.%Y")
        url_l = f'https://dnevnik2.petersburgedu.ru/api/journal/lesson/list-by-education?p_datetime_from={datem}%2000:00:00&p_datetime_to={datem}%2023:59:59&p_educations%5B%5D={person_id}'
        response = requests.post(url_l, data={}, headers=jwt_token)
        response_tasks = json.loads(response.text)
        subject_names_copy = subject_names.copy()

        url_l = f'https://dnevnik2.petersburgedu.ru/api/journal/schedule/list-by-education?p_page=1&p_datetime_from={datem}%2000:00:00&p_datetime_to={datem}%2023:59:59&p_educations%5B%5D={person_id}'
        response = requests.post(url_l, data={}, headers=jwt_token)
        response_schedule = json.loads(response.text)
        subject_names_copy = subject_names.copy()

        for i in response_schedule['data']['items']:
            if i['subject_name'] in subject_names:
                if i['subject_name'] in subject_names_copy:
                    subject_names_copy.remove(i['subject_name'])

        for i in response_tasks['data']['items']:
            if i['subject_name'] in subject_names:
                if i["tasks"]:
                    for j in i["tasks"]:
                        if j['task_name'] != None:
                            current_sub_name = i['subject_name']
                            new_tasks = [j["task_name"]]
                            Tasks[current_sub_name] = [x for x in Tasks[current_sub_name]] + new_tasks
                        if len(j["files"]) > 0:
                            nl = '\n'   
                            url_id = j["files"][0]["uuid"]
                            file_url = f'https://dnevnik2.petersburgedu.ru/api/filekit/file/download?p_uuid={url_id}'
                            current_sub_name = i['subject_name']
                            Tasks[current_sub_name] = [x for x in Tasks[current_sub_name]] + [f'Прикрепленный файл:{nl}{file_url}{nl}']

                if i['subject_name'] in subject_names_copy:
                    subject_names_copy.remove(i['subject_name'])
        subject_names = subject_names_copy

    return Tasks


async def request_data(message: types.Message, state: FSMContext):
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
    await state.update_data(jwt_token=token)

    url_l = f'https://dnevnik2.petersburgedu.ru/api/journal/institution/related-jurisdiction-list?p_page=1'
    response = requests.post(url_l, data={}, headers=token)
    first_id = json.loads(response.text)
    first_id = first_id['data']['items'][0]['id']

    url_l = f'https://dnevnik2.petersburgedu.ru/api/journal/institution/related-institution-list?p_page=1&p_jurisdictions%5B%5D={first_id}'
    response = requests.post(url_l, data={}, headers=token)
    second_id = json.loads(response.text)
    second_id = second_id['data']['items'][0]['id']

    url_l = f'https://dnevnik2.petersburgedu.ru/api/journal/group/related-group-list?p_page=1&p_jurisdictions%5B%5D={first_id}&p_institutions%5B%5D={second_id}'
    response = requests.post(url_l, data={}, headers=token)
    group_id = json.loads(response.text)
    group_id = group_id['data']['items'][0]['id']


    
    url_l = f'https://dnevnik2.petersburgedu.ru/api/journal/person/related-person-list?p_page=1&p_jurisdictions%5B%5D={first_id}&p_institutions%5B%5D={second_id}&p_groups%5B%5D={group_id}'
    response = requests.post(url_l, data={}, headers=token)
    person_id = json.loads(response.text)
    person_id = person_id['data']['items'][0]['educations'][0]['education_id']

    await state.update_data(person_id=person_id)
    await message.answer('Чтобы узнать уроки на сегодня, используй команду /lessons')


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = [
        [
            types.KeyboardButton(text="/registration"),
            types.KeyboardButton(text="/lessons")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await message.answer("Привет! Если ты еще не зашел(а) в свой аккаунт Электронного дневника, то нажми /registration. Если ты уже заходил(а) в свой аккаунт, то нажми /lessons", reply_markup=keyboard)


#async def get_lessons(state: FSMContext, ):
 #   url = "https://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD"
  #  query_parameters = {"downloadformat": "csv"}


@dp.message(Command("lessons"))
async def cmd_start(message: types.Message, state: FSMContext):
    Tasks = await get_lessons(state=state)
    nl = '\n'
    for k, v in Tasks.items():
        print(k, v)
        if len(v) == 0:
            await message.answer(f'Предмет: {k}{nl}Домашнего задания нет (¬‿¬ ){nl}')
        else:
            await message.answer(f'Предмет: {k}{nl}')
            await message.answer(nl.join(v))
        

@dp.message(Command("registration"))
async def login_step(message: types.Message, state: FSMContext):
    await message.answer(text='Привет! Напиши свой логин(email) от Электронного дневника без лишних пробелов:')
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
    await request_data(message=message, state=state)

# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_router(form_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
