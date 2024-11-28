import asyncio
import datetime
import time
from zoneinfo import ZoneInfo

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.keyboards.send_post_keyboard import send_post_base_kb, send_post_kb, kb_back_send_post
from database.db import get_button_states, add_publ_time_tg, add_publ_time_vk, get_all_publ_time

router = Router(name="Отправка поста")

msk_tz = ZoneInfo("Europe/Moscow")


class DateStates(StatesGroup):
    waiting_for_new_time = State()
    waiting_for_new_date_and_time = State()


@router.callback_query(F.data.startswith("send_post:"))
async def send_post_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    media_id = callback.data.split(":")[-1]
    await callback.message.edit_text(
        text="ᅠ                               🔝                       ᅠ",
        reply_markup=send_post_kb(media_id)
    )


@router.callback_query(F.data.startswith("send_post_now:"))
async def send_post_now_handler(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(':')[-1]
    check_publ_post(media_id=media_id, set_time_post=None)
    await callback.message.edit_reply_markup(
        reply_markup=send_post_base_kb(media_id)
    )


@router.callback_query(F.data.startswith("send_post_today:"))
async def send_post_tomorrow_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    media_id = callback.data.split(':')[-1]
    date_post = datetime.datetime.now(msk_tz).date()
    message_del_db = await callback.message.edit_text(
        f"ᅠ                               🔝                       ᅠ\n⌛️ Введите время форматом {datetime.datetime.now(msk_tz).strftime('%H:%M')}",
        reply_markup=kb_back_send_post(media_id))
    check_publ_post(media_id, date_post)
    await state.update_data(media_id=media_id, message_del_db=message_del_db.message_id)
    await state.set_state(DateStates.waiting_for_new_time)


@router.callback_query(F.data.startswith("send_post_tomorrow:"))
async def send_post_tomorrow_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    media_id = callback.data.split(':')[-1]
    date_post = datetime.datetime.now(msk_tz).date() + datetime.timedelta(days=1)
    message_del_db = await callback.message.edit_text(
        f"ᅠ                               🔝                       ᅠ\n⌛️Введите время форматом {datetime.datetime.now(msk_tz).strftime('%H:%M')}",
        reply_markup=kb_back_send_post(media_id))
    check_publ_post(media_id, date_post)
    await state.update_data(media_id=media_id, message_del_db=message_del_db.message_id)
    await state.set_state(DateStates.waiting_for_new_time)


@router.callback_query(F.data.startswith("send_post_by_time:"))
async def send_post_by_time_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    media_id = callback.data.split(':')[-1]
    message_del_db = await callback.message.edit_text(
        text=f'ᅠ                               🔝                       ᅠ\n⌛️Введите дату и время форматом {datetime.datetime.now(msk_tz).strftime("%Y-%m-%d %H:%M")}',
        reply_markup=kb_back_send_post(media_id))
    await state.update_data(media_id=media_id, message_del_db=message_del_db.message_id)
    await state.set_state(DateStates.waiting_for_new_date_and_time)


@router.message(DateStates.waiting_for_new_date_and_time)
async def handle_new_signature(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_id = data['media_id']
    message_del_db = data['message_del_db']
    await message.delete()
    if len(message.text) < 15:
        date_post = '20' + message.text[:2] + '-' + message.text[3:5] + '-' + message.text[6:8] + ' ' + message.text[
                                                                                                        9:11] + ':' + message.text[
                                                                                                                      -2:] + ':00'
    else:
        date_post = message.text[:4] + '-' + message.text[5:7] + '-' + message.text[8:10] + ' ' + message.text[
                                                                                                  11:13] + ':' + message.text[
                                                                                                                 -2:] + ':00'
    check_publ_post(media_id, date_post)
    time_now = datetime.datetime.now(msk_tz).replace(tzinfo=None)
    date_post = datetime.datetime.strptime(date_post, '%Y-%m-%d %H:%M:%S')
    if time_now > date_post:
        mg_del = await message.answer(text="⚠️ Дата не может быть прошедшей!")
        await asyncio.sleep(2)
        await message.bot.delete_message(chat_id=message.chat.id,
                                         message_id=mg_del.message_id)
        await state.clear()
        return
    else:
        await message.bot.edit_message_text(text=f"✅ Пост будет отправлен {date_post}",
                                            chat_id=message.chat.id,
                                            message_id=message_del_db,
                                            reply_markup=send_post_base_kb(media_id)
                                            )


@router.message(DateStates.waiting_for_new_time)
async def handle_new_signature(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_id = data.get('media_id')
    message_del_db = data.get('message_del_db')
    await message.delete()
    publ_date = get_all_publ_time(media_id)
    states = get_button_states(media_id)
    if states[0] == "off" or states[1] == "off":
        if states[0] == "off":  # Установка времени для тг
            if len(publ_date[0]) > 10:  # "YYYY-MM-DD HH:MM:SS"
                date_time_str = publ_date[0]
                date_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
            else:
                # Строка содержит только дату
                date_time_str = publ_date[0]
                date_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d")

            try:
                time_part = datetime.time(int(message.text[:2]), int(message.text[-2:]))
            except ValueError:
                mg_del = await message.answer(text=f"⚠️ Неправильно указано время!\nУкажите в формате {datetime.datetime.now(msk_tz).strftime('%H:%M')} (чч:мм)")
                await asyncio.sleep(2)
                await message.bot.delete_message(chat_id=message.chat.id,
                                                 message_id=mg_del.message_id)
                return

            publ_time = datetime.datetime.combine(date_time.date(), time_part)

            time_now = datetime.datetime.now(msk_tz).replace(tzinfo=None)
            if time_now > publ_time:
                mg_del = await message.answer(text="⚠️ Дата не может быть прошедшей!")
                await asyncio.sleep(2)
                await message.bot.delete_message(chat_id=message.chat.id,
                                                 message_id=mg_del.message_id)
                return
            else:
                check_publ_post(media_id=media_id, set_time_post=publ_time)

        if states[1] == "off":  # Установка времени для вк
            if len(publ_date[1]) > 10:  # "YYYY-MM-DD HH:MM:SS"
                date_time_str = publ_date[1]
                date_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
            else:
                # Строка содержит только дату
                date_time_str = publ_date[1]
                date_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d")

            try:
                time_part = datetime.time(int(message.text[:2]), int(message.text[-2:]))
            except ValueError:
                mg_del = await message.answer(text=f"⚠️ Неправильно указано время!\nУкажите в формате {datetime.datetime.now(msk_tz).strftime('%H:%M')} (чч:мм)")
                await asyncio.sleep(2)
                await message.bot.delete_message(chat_id=message.chat.id,
                                                 message_id=mg_del.message_id)
                return

            publ_time = datetime.datetime.combine(date_time.date(), time_part)

            time_now = datetime.datetime.now(msk_tz).replace(tzinfo=None)
            if time_now > publ_time:
                mg_del = await message.answer(text="⚠️ Дата не может быть прошедшей!")
                await asyncio.sleep(2)
                await message.bot.delete_message(chat_id=message.chat.id,
                                                 message_id=mg_del.message_id)
                return
            else:
                check_publ_post(media_id=media_id, set_time_post=publ_time)

        await message.bot.edit_message_text(text=f"✅ Пост будет отправлен {publ_time}",
                                            chat_id=message.chat.id,
                                            message_id=message_del_db,
                                            reply_markup=send_post_base_kb(media_id))
        await state.clear()

    else:
        await message.bot.edit_message_text(text=f"✅ Все посты отправлены!",
                                            chat_id=message.chat.id,
                                            message_id=message_del_db,
                                            reply_markup=send_post_base_kb(media_id))
        await state.clear()


@router.callback_query(F.data == "error")
async def middleware_error(callback: types.CallbackQuery, ) -> None:
    mess = await callback.message.answer("⛔️ Пост уже был опубликован!")
    time.sleep(2)
    await callback.bot.delete_message(chat_id=mess.chat.id,
                                      message_id=mess.message_id)


def check_publ_post(media_id: str, set_time_post: datetime):
    states = get_button_states(media_id)
    if states[0] == 'off':
        add_publ_time_tg(media_id=media_id, publ_time_tg=set_time_post)
    if states[1] == 'off':
        add_publ_time_vk(media_id=media_id, publ_time_vk=set_time_post)
