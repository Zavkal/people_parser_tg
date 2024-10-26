from aiogram import F, Router, types

router = Router(name="Отправка поста в ВК")


@router.callback_query(F.data == "send_to_vk")
async def send_to_vk_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.answer(
        text="Пост отправлен в ВК"
    )
