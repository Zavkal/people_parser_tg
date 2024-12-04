import asyncio
import os

from pyrogram import Client

from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F, types, flags
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from bot.keyboards.parser_kb import get_sources_for_del, get_started_kb
from database.clients import clients
from database.db import add_source, del_source, get_sources, get_parser_info, add_parser_info, delete_parser_info, \
    get_all_parser_info, get_source, select_chat, delete_all_parser_info

from bot.keyboards.admin_kb import settings_parser_kb, back_add_sources

from bot.middleware.parser_operations import get_all_sources, check_channel, get_sources_ids, parser, stop_parsers


router = Router(name="Парсер")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

PHOTO_PARSER = FSInputFile(path=os.path.join(BASE_DIR, "img", "sources.jpg"))


class AddSource(StatesGroup):
    add = State()


@router.callback_query(F.data == "delete_settings")
async def delete_message_(callback_query: types.CallbackQuery):
    await callback_query.message.delete()


@router.callback_query(F.data == "source_admin")
@flags.authorization(all_rights=True)
async def settings_parser(callback: types.CallbackQuery):
    sources = get_all_sources()
    if sources:
        await callback.message.edit_caption(caption=sources, reply_markup=settings_parser_kb())
    else:
        await callback.message.edit_caption(caption='Источники отсутствуют', reply_markup=settings_parser_kb())


@router.message(AddSource.add, F.text)
@flags.authorization(all_rights=True)
async def add_sources(message: types.Message, state: FSMContext):
    data = await state.get_data()
    client = clients.get("client")
    chanel = message.text
    if await check_channel(client=client, username=chanel):
        if not get_source(chanel):
            add_source(title=chanel)
            await state.clear()
            await message.bot.delete_message(chat_id=message.chat.id, message_id=data.get("message_id"))
            await message.answer_photo(caption=get_all_sources(), reply_markup=settings_parser_kb(), photo=PHOTO_PARSER)
        else:
            bot_message = await message.answer(text="Такой канал уже есть в источниках")
            await asyncio.sleep(5)
            await bot_message.delete()
        await message.delete()
    else:
        bot_message = await message.answer(text="Канал не найден, попробуйте ещё раз")
        await message.delete()
        await asyncio.sleep(5)
        await bot_message.delete()


@router.callback_query(F.data == "back_add_sources")
@flags.authorization(post_rights=True)
async def back_settings_parser(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    sources = get_all_sources()
    if sources:
        await callback_query.message.edit_caption(caption=sources, reply_markup=settings_parser_kb())
    else:
        await callback_query.message.edit_caption(caption='Источники отсутствуют', reply_markup=settings_parser_kb())


@router.callback_query(AddSource.add)
@flags.authorization(all_rights=True)
async def add_sources_valid(callback_query: types.CallbackQuery):
    await callback_query.answer(text="Ожидаю юзернейм канала")


@router.callback_query(F.data == "del_source")
@flags.authorization(post_rights=True)
async def start_del_sources(callback_query: types.CallbackQuery):
    sources = get_all_sources()
    if sources:
        await callback_query.message.edit_caption(caption='Какой источник удалить?',
                                                  reply_markup=get_sources_for_del())
    else:
        await callback_query.answer("Отсутсвуют источники")


@router.callback_query(F.data == "add_source")
@flags.authorization(post_rights=True)
async def add_sources_(callback_query: types.CallbackQuery, state: FSMContext):
    client = clients.get("client")
    if client:
        await callback_query.message.edit_caption(caption='Введите юзернейм канала, без @',
                                                  reply_markup=back_add_sources())
        await state.set_state(AddSource.add)
        await state.update_data({"message_id": callback_query.message.message_id})
    else:
        await callback_query.answer(text="Установите или перезапустите юзербота")


@router.callback_query(F.data.startswith("source_del_"))
@flags.authorization(post_rights=True)
async def del_sources(callback_query: types.CallbackQuery):
    source_id = callback_query.data.split("_")[-1]
    source_title = callback_query.data.split("_")[-2]
    del_source(source_id)
    delete_parser_info(source_title)
    sources = get_sources()
    if sources:
        await callback_query.message.edit_caption(caption='Какой источник удалить?',
                                                  reply_markup=get_sources_for_del())
    else:
        await callback_query.message.edit_caption(caption='Источники отсутствуют', reply_markup=settings_parser_kb())


@router.callback_query(F.data == "start_parser")
@flags.authorization(all_rights=True)
async def start_parser(callback_query: types.CallbackQuery):
    if not get_sources():
        await callback_query.answer("Отсутсвуют источники")
    elif not clients.get("client"):
        await callback_query.answer(text="Установите или перезапустите юзербота")
    else:
        await callback_query.message.edit_caption(caption='Какой запустить?',
                                                  reply_markup=get_started_kb("start"))


@router.callback_query(F.data == "start_all_parser")
@flags.authorization(all_rights=True)
async def start_all_parsers(callback_query: types.CallbackQuery):
    sources = get_sources()
    parsers = get_all_parser_info()
    if len(sources) == len(parsers):
        await callback_query.answer("Уже все запущены")
    else:
        if not select_chat():
            return await callback_query.answer("Настойте чат в админ панели")
        for _id, title in sources:
            if not get_parser_info(title):
                add_parser_info(title)
        await callback_query.message.edit_caption(caption='Какой запустить?',
                                                  reply_markup=get_started_kb("start"))
        await parser()


@router.callback_query(F.data == "stop_all_parser")
@flags.authorization(all_rights=True)
async def stop_all_parsers(callback_query: types.CallbackQuery):
    parsers = get_all_parser_info()
    if len(parsers) == 0:
        await callback_query.answer("Уже все остановлены")
    else:
        delete_all_parser_info()
        await callback_query.message.edit_caption(caption='Какой остановить?',
                                                  reply_markup=get_started_kb("stop"))


@router.callback_query(F.data.startswith("start_source_"))
@flags.authorization(post_rights=True)
async def start_parser_for_id(callback_query: types.CallbackQuery):
    title = callback_query.data.split("start_source_")[-1]
    is_started = get_parser_info(title)
    if not is_started:
        add_parser_info(title)
        ids = get_sources_ids()
        client: Client = clients.get("client")
        if not select_chat():
            return await callback_query.answer("Настойте чат в админ панели")
        if ids and client:
            await callback_query.message.edit_caption(caption='Какой запустить?',
                                                      reply_markup=get_started_kb("start"))
            await parser()
    elif is_started:
        await callback_query.answer(text="Уже запущен")


@router.callback_query(F.data == "stop_parser")
@flags.authorization(all_rights=True)
async def stop_parser(callback_query: types.CallbackQuery):
    if not get_sources():
        await callback_query.answer("Отсутсвуют источники")
    else:
        await callback_query.message.edit_caption(caption='Какой остановить?',
                                                  reply_markup=get_started_kb("stop"))


@router.callback_query(F.data.startswith("stop_source_"))
@flags.authorization(post_rights=True)
async def stop_parser_for_id(callback_query: types.CallbackQuery):
    title = callback_query.data.split("stop_source_")[-1]
    is_started = get_parser_info(title)
    if is_started:
        delete_parser_info(title)
        await callback_query.message.edit_caption(caption='Какой остановить?',
                                                  reply_markup=get_started_kb("stop"))
    else:
        await callback_query.answer(text="Уже остановлен")
