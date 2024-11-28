from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.base_post_working_keyboard import base_post_working_kb
from bot.keyboards.start_keyboard import start_kb_middleware

from database.db import  select_who_worked, add_who_worked, \
    get_post_media_by_media_id, delete_who_worked

router = Router(name="Начальная работа с постом")


@router.callback_query(F.data.startswith("start_working:"))
async def base_post_working_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Комманда запуска бота"""
    await state.clear()
    media_id = callback.data.split(":")[1]
    all_message = get_post_media_by_media_id(media_id)
    who_worked = select_who_worked(mess_id=all_message[0]["mess_first_id"])

    if not who_worked or who_worked[0]:
        await callback.message.edit_text("ᅠ                               🔝                       ᅠ",
                                         reply_markup=base_post_working_kb(media_id=media_id))
        add_who_worked(user_id=all_message[0]['chat_id'],
                       caption=all_message[0]['content'],
                       mess_id=all_message[0]['mess_first_id'])
    elif str(callback.message.from_user.id):
        await callback.message.edit_text("ᅠ                               🔝                       ᅠ",
                                         reply_markup=base_post_working_kb(media_id=media_id))
    else:
        await callback.answer("Уже взят другим в работу")


@router.callback_query(F.data.startswith("start_kb_middleware:"))
async def base_start_kb_middleware(callback: types.callback_query) -> None:
    media_id = callback.data.split(":")[1]
    all_message = get_post_media_by_media_id(media_id)
    delete_who_worked(mess_id=all_message[0]["mess_first_id"])
    await callback.message.edit_text(text="ᅠ                               🔝                       ᅠ",
                                     reply_markup=start_kb_middleware(media_id))
