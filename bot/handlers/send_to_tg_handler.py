from aiogram import F, Router, types

router = Router(name="Отправка поста в ТГ")


@router.callback_query(F.data == "send_to_tg")
async def send_to_tg_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.answer(
        text="Пост отправлен в ТГ"
    )
