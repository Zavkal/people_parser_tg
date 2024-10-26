from aiogram import F, Router, types

from keyboards.send_post_keyboard import send_post_base_kb, send_post_by_time_kb, send_post_kb, send_post_tomorrow_kb

router = Router(name="Отправка поста")


@router.callback_query(F.data == "send_post")
async def send_post_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_reply_markup(
        reply_markup=send_post_kb
    )


@router.callback_query(F.data == "send_post_now")
async def send_post_now_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_reply_markup(
        reply_markup=send_post_base_kb
    )


@router.callback_query(F.data == "send_post_tomorrow")
async def send_post_tomorrow_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_reply_markup(
        reply_markup=send_post_tomorrow_kb
    )


@router.callback_query(F.data == "send_post_by_time")
async def send_post_by_time_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_reply_markup(
        reply_markup=send_post_by_time_kb
    )
