import sqlite3

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.handlers.person.hero import can_use_item
from AzeibarjanWarBOT.keyboards import default, inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_trick, get_user_info

cb_know_items = CallbackData("trick", "buttons")

# Боевые приемы, активные приемы
@dp.message_handler(IsPrivate(), text=[strings.trainer_button_list[0], strings.trainer_button_list[1]])
async def tricks_hero(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    tricks = user_info.get_tricks
    trick_list = []
    for i in tricks:
        trick = await get_trick(i) if i is not None else None
        trick_list.append(trick)

    await bot.send_message(message.from_user.id, await strings.trainer_tricks_list(trick_list),
                           reply_markup=await default.hero_tricks_menu())


@dp.message_handler(IsPrivate(), text_startswith=["/unsetcombo", "/setcombo"])
async def unset_set_command(message: types.Message):
    # /setcombo1_79 | /unsetcombo1_79
    try:
        user_info = await get_user_info(message.from_user.id)
        type = "set" if message.text[1:4] == "set" else "unset"
        text_split = message.text.split("_")
        trick_slot = int(text_split[0][-1])
        # Ставим прием
        if type == "set":
            trick_id = int(text_split[1])

            trick_name = await DB.get_current_item_from_inventory(user_info.nickname, trick_id)
            trick_name = trick_name[3]


            result = await can_use_item(trick_name, user_info, "trick")
            if not result:
                await DB.update_trick(user_info.id, trick_slot, trick_name)
                await message.reply(strings.you_successfully_use_it[2])
            else:
                await message.reply(result)
        # Снимаем прием ставим None
        elif type == "unset":
            await DB.update_trick(user_info.id, trick_slot)
            await message.reply(strings.you_successfully_use_it[3])
    except (IndexError, ValueError, sqlite3.OperationalError, TypeError):
        await bot.send_message(message.from_user.id, strings.not_aviable_inp)

# Сменить прием
@dp.message_handler(IsPrivate(), text_startswith=strings.trainer_button_list[3])
async def change_trick(message: types.Message):
    trick_number = int(message.text[-1])

    user_info = await get_user_info(message.from_user.id)
    tricks = await DB.get_current_items(user_info.nickname, "trick")

    text = f"<b>{strings.trainer_button_list[3]}{trick_number}</b>\n\n"

    result = await generate_tricks_list_setter(tricks, user_info.get_tricks[trick_number - 1], trick_number, user_info)

    keyb = await inline.text_buttons_keyboard_trick(result, 0, 4, cb_know_items, trick_number)

    if 4 >= len(result) > 0:
        await bot.send_message(message.from_user.id, text + keyb[1])
    # Случай если приемов 0, просто пишем
    elif len(result) == 0:
        await bot.send_message(message.from_user.id, text + strings.you_not_have_any_tricks)
    # Если приемов уже больше 4, то добавляем кнопки
    else:
        await bot.send_message(message.from_user.id, text + keyb[1], reply_markup=keyb[0])


# Кнопока изученые приемы
@dp.message_handler(IsPrivate(), text=strings.trainer_button_list[2])
async def tricks_know(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    tricks = await DB.get_current_items(user_info.nickname, "trick")

    tricks_list = await generate_tricks_list(tricks, user_info)

    # Текст изученые приемы
    text = f"{strings.trainer_button_list[2]}\n\n"
    # Получим текст, кнопки
    keyb = await inline.text_buttons_keyboard_trick(tricks_list, 0, 4, cb_know_items)
    # Если приемов не больше 4 и не 0, сообщение без кнопок
    if 4 >= len(tricks_list) > 0:
        await bot.send_message(message.from_user.id, text + keyb[1])
    # Случай если приемов 0, просто пишем
    elif len(tricks_list) == 0:
        await bot.send_message(message.from_user.id, text + strings.you_not_have_any_tricks)
    # Если приемов уже больше 4, то добавляем кнопки
    else:
        await bot.send_message(message.from_user.id, text + keyb[1], reply_markup=keyb[0])


# Нажатие на стрелочки перелистывания списка приемов
@dp.callback_query_handler(cb_know_items.filter())
async def know_items(call: types.CallbackQuery):
    info = call.data.split(":")[1].split("-")
    user_info = await get_user_info(call.from_user.id)
    action = info[3]
    trick_number = int(info[2])
    # Список с trick информацией
    tricks = await DB.get_current_items(user_info.nickname, "trick")

    first_num = int(info[0]) + 4 if action == "next" else int(info[0]) - 4
    last_num = int(info[1]) + 4 if action == "next" else int(info[1]) - 4

    if trick_number == 0:
        text = f"{strings.trainer_button_list[2]}\n\n"
        tricks_list = await generate_tricks_list(tricks, user_info)
        keyb = await inline.text_buttons_keyboard_trick(tricks_list, first_num, last_num, cb_know_items)

    else:
        text = f"{strings.trainer_button_list[3]} {trick_number}\n\n"
        tricks_list = await generate_tricks_list_setter(tricks, user_info.get_tricks[trick_number - 1], trick_number, user_info)
        keyb = await inline.text_buttons_keyboard_trick(tricks_list, first_num, last_num, cb_know_items, trick_number)

    # Если список не пустой
    if keyb[1]:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text + keyb[1],
                                    reply_markup=keyb[0])
    # Если список пустой, пишем что последняя или первая страница исходя из action
    else:
        await call.answer(strings.last_page if action == "next" else strings.first_page)


async def generate_tricks_list(tricks, user_info):
    """Получаем на входе сырой список tricks id, после чего получаем информацию о этом элементе"""
    tricks_list = []
    for i in tricks:
        trick = await get_trick(i[0])
        result_use = not bool(await can_use_item(trick.id, user_info, "trick"))
        tricks_list.append(await trick.get_item_desc_tricks(user_info, result_use))
    return tricks_list


async def generate_tricks_list_setter(tricks, current_trick_id, trick_number, user: User):
    async def get_trick_desc(trick_id, trick_use, item_id):
        current_trick = await get_trick(trick_id)
        use = strings.trick[1] if trick_use is False else strings.trick[0]
        action = strings.trick[3] if trick_use is False else strings.trick[2]
        action_command = "/setcombo" if trick_use is False else "/unsetcombo"
        return f"{use} <b>{current_trick.title}</b>\n{current_trick.description}\n{action} {action_command}{trick_number}_{item_id}\n"

    tricks_list = []

    if current_trick_id is not None:
        trick_inv_id = await DB.get_item_inventory_name(user.nickname, current_trick_id)
        tricks_list.append(await get_trick_desc(current_trick_id, True, trick_inv_id))

    for i in tricks:
        if i is not None and i[0] not in user.get_tricks:
            tricks_list.append(await get_trick_desc(i[0], False, i[1]))

    return tricks_list
