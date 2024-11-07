import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.keyboards.send_post_keyboard import send_post_base_kb, send_post_by_time_kb, send_post_kb, \
    send_post_tomorrow_kb, send_post_today_kb, kb_back_send_post
from bot.middleware.check_media import check_media_post
from database.db import get_button_states, add_publ_time_tg, add_publ_time_vk, get_all_publ_time

router = Router(name="Отправка поста")

msk_tz = ZoneInfo("Europe/Moscow")


class DateStates(StatesGroup):
    waiting_for_new_date = State()


@router.callback_query(F.data.startswith("send_post:"))
async def send_post_handler(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(":")[-1]
    await callback.message.edit_reply_markup(
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
async def send_post_tomorrow_handler(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(':')[-1]
    date_post = datetime.datetime.now(msk_tz).date()
    check_publ_post(media_id, date_post)
    await callback.message.edit_reply_markup(
        reply_markup=send_post_tomorrow_kb(media_id)
    )


@router.callback_query(F.data.startswith("send_post_tomorrow:"))
async def send_post_tomorrow_handler(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(':')[-1]
    date_post = datetime.datetime.now(msk_tz).date() + datetime.timedelta(days=1)
    check_publ_post(media_id, date_post)
    await callback.message.edit_reply_markup(
        reply_markup=send_post_today_kb(media_id)
    )


@router.callback_query(F.data.startswith("send_post_by_time:"))
async def send_post_by_time_handler(callback: types.CallbackQuery, ) -> None:
    media_id = callback.data.split(':')[-1]
    await callback.message.edit_reply_markup(
        reply_markup=send_post_by_time_kb(media_id)
    )


@router.callback_query(F.data.startswith("choose_time:"))
async def choose_time_for_publish(callback: types.CallbackQuery, state: FSMContext) -> None:
    media_id = callback.data.split(':')[-1]
    message_del_db = await callback.message.edit_reply_markup(reply_markup=kb_back_send_post(media_id))
    await state.update_data(media_id=media_id, message_del_db=message_del_db.message_id)
    await state.set_state(DateStates.waiting_for_new_date)


@router.message(DateStates.waiting_for_new_date)
async def handle_new_signature(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_id = data.get('media_id')
    message_del_db = data.get('message_del_db')
    await message.delete()
    publ_date = get_all_publ_time(media_id)
    if publ_date[0]:
        date = datetime.datetime.strptime(publ_date[0], "%Y-%m-%d").date()
        time_part = datetime.time(int(message.text[:2]), int(message.text[-2:]))
        publ_time = datetime.datetime.combine(date, time_part)
        add_publ_time_tg(media_id=media_id, publ_time_tg=publ_time)
    if publ_date[1]:
        date = datetime.datetime.strptime(publ_date[1], "%Y-%m-%d").date()
        time_part = datetime.time(int(message.text[:2]), int(message.text[-2:]))
        publ_time = datetime.datetime.combine(date, time_part)
        add_publ_time_vk(media_id=media_id, publ_time_vk=publ_time)

    await message.bot.edit_message_text(text="🔝ㅤ",
                                        chat_id=message.chat.id,
                                        message_id=message_del_db,
                                        reply_markup=send_post_base_kb(media_id))
    await state.clear()


def check_publ_post(media_id: str, set_time_post: datetime):
    states = get_button_states(media_id)
    if states[0] == 'off':
        add_publ_time_tg(media_id=media_id, publ_time_tg=set_time_post)
    if states[1] == 'off':
        add_publ_time_vk(media_id=media_id, publ_time_vk=set_time_post)
