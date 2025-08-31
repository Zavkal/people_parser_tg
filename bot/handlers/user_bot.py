import asyncio
import logging
import os

from aiogram import Router, F, types, flags
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, CallbackQuery
from aiogram.utils.markdown import hlink
from pyrogram import Client

from database.clients import clients
from database.db import select_user, add_user, get_sources, update_user, select_user_with_param, get_all_parser_info, \
    delete_all_users_bot
from bot.keyboards.admin_kb import back_settings_user, start_admin_panel_kb, settings_user_already
from bot.middleware.parser_operations import stop_parsers, delete_session, parser, TaskManager

router = Router(name="Юзербот")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

PHOTO_USER = FSInputFile(path=os.path.join(BASE_DIR, "img", "user_data.jpg"))


class AddUserData(StatesGroup):
    add = State()
    phone_code = State()


@router.callback_query(F.data == "settings_data")
@flags.authorization(all_rights=True)
async def set_userdata(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_caption(
        caption=f"Ознакомьтесь с {hlink(title='инструкцией', url='https://docs.google.com/document/d/1cqG9Kiz0EsoVCOmxNMZ-QLwV2LpczhycTUZ7PU_IjaU/edit?usp=sharing')}, "
                f"далее перейдите по {hlink('ссылке', url='https://my.telegram.org/auth')} и введите нужные данные ниже в формате:\n"
                f"api_id,api_hash,номер_телефона",
        parse_mode="html",
        reply_markup=back_settings_user())
    await state.update_data({"call_id": callback_query.message.message_id})
    await state.set_state(AddUserData.add)


@router.message(AddUserData.add, F.text)
@flags.authorization(all_rights=True)
async def set_data(message: types.Message, state: FSMContext):
    try:
        session_dir = "sessions"
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        api_id, api_hash, phone = message.text.split(",")
        user = select_user_with_param(api_id)
        session_file = os.path.join(session_dir, api_id)
        if user:
            bot_mess = await message.answer(text="Этот аккаунт уже используется")
            await asyncio.sleep(3)
            await bot_mess.delete()
        else:
            client = Client(name=session_file, api_id=api_id, api_hash=api_hash, phone_number=phone)
            await client.connect()
            send_code = await client.send_code(phone)
            await state.update_data(
                {"code": send_code, "client": client, "phone_number": phone, "api_id": api_id, "api_hash": api_hash})
            await state.set_state(AddUserData.phone_code)
            bot_mess = await message.answer(text="Введите код")
            await asyncio.sleep(8)
            await message.delete()
            await bot_mess.delete()
    except Exception as ex:
        logging.error(ex)
        bot_message = await message.answer(text="Данные не верные",
                                           reply_markup=start_admin_panel_kb(message.from_user.id))
        await state.clear()
        await asyncio.sleep(2)
        await bot_message.delete()


@router.callback_query(AddUserData.add, F.data == "back_settings_data")
@flags.authorization(all_rights=True)
async def back_setting_user(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    data = select_user()
    if not data:
        await callback_query.message.edit_caption(caption="Данные отсутствуют", reply_markup=settings_user_already())
    else:
        await callback_query.message.edit_caption(caption=f"Телефон: {data[2]}\n"
                                                          f"API_ID: {data[0]}\n"
                                                          f"API_HASH: {data[1]}\n",
                                                  reply_markup=settings_user_already())


@router.callback_query(AddUserData.add)
@flags.authorization(all_rights=True)
async def set_id_hash_valid(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Введите api_id,api_hash,номер_телефона")


@router.message(AddUserData.phone_code, F.text)
@flags.authorization(all_rights=True)
async def set_phone_code(message: types.Message, state: FSMContext):
    phone_code = message.text
    data = await state.get_data()
    client, send_code, phone = data.get("client"), data.get("code"), data.get("phone_number")
    try:
        user = await client.sign_in(phone, send_code.phone_code_hash, phone_code)
        if user:
            sources = get_sources()
            stop_parsers(sources)
            user = select_user()
            if user:
                update_user(data.get("api_id"), data.get("api_hash"), phone)
                delete_session(user[0])
                bot_mess = await message.answer(text="Данные сохранены",
                                                reply_markup=start_admin_panel_kb(message.from_user.id))

            else:
                add_user(data.get("api_id"), data.get("api_hash"), phone)
                bot_mess = await message.answer(text="Данные сохранены",
                                                reply_markup=start_admin_panel_kb(message.from_user.id))
            await message.bot.edit_message_caption(chat_id=message.chat.id,
                                                   message_id=data.get("call_id"),
                                                   caption=f"Телефон: {phone}\n"
                                                           f"API_ID: {data.get('api_id')}\n"
                                                           f"API_HASH: {data.get('api_hash')}\n",
                                                   reply_markup=settings_user_already())

            clients["client"] = client
            await asyncio.sleep(2)
            await message.delete()
            await bot_mess.delete()
    except Exception as ex:
        logging.error(ex)
        bot_mess = await message.answer(text="Данные не верные",
                                        reply_markup=start_admin_panel_kb(message.from_user.id))
        await client.disconnect()
        delete_session(data.get("api_id"))
        await asyncio.sleep(2)
        await bot_mess.delete()
    finally:
        await state.clear()


@router.callback_query(AddUserData.phone_code)
@flags.authorization(all_rights=True)
async def set_phone_code_valid(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Я ожидаю код")


@router.callback_query(F.data == "restart_client")
@flags.authorization(all_rights=True)
async def restart_client_user(callback_query: types.CallbackQuery):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    session_dir = os.path.join(BASE_DIR, "sessions")
    # Убедимся, что папка для сессий существует
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)

    client = clients.get("client")
    user = select_user()
    active_parsers = get_all_parser_info()

    if user:
        session_file = os.path.join(session_dir, f"{user[0]}")
        session_journal_file = os.path.join(session_dir, f"{user[0]}.session-journal")

        if not active_parsers:
            if os.path.exists(session_journal_file):
                try:
                    await client.stop()
                    await client.start()
                    clients["client"] = client
                except:
                    client = Client(name=session_file, api_id=int(user[0]), api_hash=user[1])
                    await client.start()
                    clients["client"] = client

            elif not client:
                client = Client(name=session_file, api_id=int(user[0]), api_hash=user[1])
                try:
                    await client.start()
                    clients["client"] = client
                except Exception as e:
                    mess_del = await callback_query.message.answer(text=f"Сессия от бота сломана. Ошибка {e}")
                    await asyncio.sleep(5)
                    await callback_query.bot.delete_message(chat_id=mess_del.chat.id,
                                                            message_id=mess_del.message_id)
                    if os.path.exists(session_file):
                        os.remove(session_file)
                    delete_all_users_bot()
                    await callback_query.answer(text="Данные юзербота и файлы удалены.")
                    return
            await callback_query.answer(text="Клиент перезапущен")
        else:
            await callback_query.answer(text="Остановите все парсеры источников")
    else:
        await callback_query.answer(text='У вас нет юзербота для рестарта.')


@router.callback_query(F.data == "go_in_userbot_kb")
async def send_userbot_settings(callback: CallbackQuery):
    data = select_user()
    if not data:
        await callback.message.edit_caption(caption="Данные отсутствуют",
                                            reply_markup=settings_user_already())
    else:
        await callback.message.edit_caption(caption=f"Телефон: {data[2]}\n"
                                                    f"API_ID: {data[0]}\n"
                                                    f"API_HASH: {data[1]}\n",
                                            reply_markup=settings_user_already())


@router.callback_query(F.data == "data_userbot")
async def send_userbot_settings(callback_query: CallbackQuery):
    data = select_user()
    if not data:
        mess_del = await callback_query.message.answer(text="Данные отсутствуют")
        await asyncio.sleep(2)
        await callback_query.message.bot.delete_message(chat_id=mess_del.chat.id,
                                                        message_id=mess_del.message_id)
    else:
        await callback_query.message.edit_caption(caption=f"Телефон: {data[2]}\n"
                                                          f"API_ID: {data[0]}\n"
                                                          f"API_HASH: {data[1]}\n",
                                                  reply_markup=settings_user_already())



@router.callback_query(F.data == "soft_start")
async def soft_start(callback_query: CallbackQuery):
    TaskManager.start()
    await callback_query.answer('Парсер запущен!')


@router.callback_query(F.data == "soft_stop")
async def soft_stop(callback_query: CallbackQuery):
    TaskManager.stop()
    await callback_query.answer('Парсер остановлен!')