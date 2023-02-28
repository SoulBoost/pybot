from typing import Text

from create_bot import dp, bot, CHANNEL_ID
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from database import sqlite_db
from keyboards import kb_client, kb_exit


# exit
@dp.message_handler(state="*", commands='exit')
@dp.message_handler(Text(equals='exit', ignore_case=True), state="*")
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK', reply_markup=kb_client)


class TakeCart(StatesGroup):
    nameTake = State()


#
@dp.message_handler(text='Взять')
async def take_start(message: types.Message):
    await TakeCart.nameTake.set()
    await message.reply("Укажите номер картриджа: ", reply_markup=kb_exit)


@dp.message_handler(state=TakeCart.nameTake)
async def getname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['nameTake'] = message.text
    await sqlite_db.sql_take(state)
    await bot.send_message(message.from_user.id, f'Вы взяли один картридж  - {data["nameTake"]}',
                           reply_markup=kb_client)
    await state.finish()


class PutCart(StatesGroup):
    namePut = State()

@dp.message_handler(text = "Положить")
async def put_start(message: types.Message):
    await PutCart.namePut.set()
    await message.reply("Укажите номер картриджа: ", reply_markup=kb_exit)

@dp.message_handler(state=PutCart.namePut)
async def getputname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['namePut'] = message.text
    await sqlite_db.sql_put(state)
    await bot.send_message(message.from_user.id, f'Вы положили картридж - {data["namePut"]}', reply_markup=kb_client)

    await state.finish()






class FSMAdmin(StatesGroup):
    name = State()
    count = State()


# Добавление нового картриджа
# @dp.message_handler(commands="Добавить", state=None)
async def cm_start(message: types.Message):
    await FSMAdmin.name.set()
    await message.reply('Введите название:', reply_markup=kb_exit)


# Ответ от пользователя
# @dp.message_handler(state=FSMAdmin.name)
async def name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.reply("Количество на данный момент", reply_markup=kb_exit)


# 2 ответ
# @dp.message_handler(state=FSMAdmin.count)
async def count(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['count'] = int(message.text)

    await sqlite_db.sql_add_command(state)
    await bot.send_message(message.from_user.id, 'Добавлено', reply_markup=kb_client)
    await state.finish()


# Регистрация хендлеров
def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start, text='Добавить новый', state=None)
    dp.register_message_handler(name, state=FSMAdmin.name)
    dp.register_message_handler(count, state=FSMAdmin.count)