from aiogram import F, Router, types

from keyboards.change_post_keyboard import (
    back_to_change_description_kb, change_description_kb,
    change_media_kb,
    change_post_kb, change_text_kb
)

router = Router(name="Изменение поста")


@router.callback_query(F.data == "change_post")
async def change_post_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_reply_markup(
        reply_markup=change_post_kb
    )


# ====================================DESCRIPTION====================================================
@router.callback_query(F.data == "change_description")
async def change_description_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_reply_markup(
        reply_markup=change_description_kb
    )


@router.callback_query(F.data == "add_description")
async def add_description_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_text(
        text="Введите новое описание",
        reply_markup=back_to_change_description_kb
    )


@router.callback_query(F.data == "remove_description")
async def remove_description_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_text(
        text="Удалить описание",
        reply_markup=back_to_change_description_kb
    )


# ====================================MEDIA====================================================
@router.callback_query(F.data == "change_media")
async def change_media_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_text(
        text="Отправьте новое медиа",
        reply_markup=change_media_kb
    )


# ====================================TEXT====================================================
@router.callback_query(F.data == "change_text")
async def change_text_handler(
    callback: types.CallbackQuery,
) -> None:
    await callback.message.edit_text(
        text="Отправьте новый текст",
        reply_markup=change_text_kb
    )
