import asyncio

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info, get_resource

cb_move_items = CallbackData("move", "item")


@dp.message_handler(IsPrivate(), text=strings.hero_buttots_keyb[3])
async def res(message: types.Message):
    """Кнопка Ресурсы"""
    user_info = await get_user_info(message.from_user.id)
    await bot.send_message(message.chat.id, strings.resources_text,
                           reply_markup=await inline.resources_keyboard(user_info.nickname))


@dp.callback_query_handler(text="to_res")
async def to_resources(call: types.CallbackQuery):
    """Кнопка к ресурсам"""
    user_info = await get_user_info(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id, text=strings.resources_text,
                                reply_markup=await inline.resources_keyboard(user_info.nickname),
                                message_id=call.message.message_id)


@dp.callback_query_handler(text=strings.item_types_res)
async def craft_res(call: types.CallbackQuery):
    """Крафтовые ресурсы inline кнопка"""
    user_info = await get_user_info(call.from_user.id)
    res_list = await DB.get_resources(user_info.nickname, call.data)

    count_items_res_list = len(res_list)

    if count_items_res_list <= 5:
        reply_markup = await inline.get_one_item_keyb(strings.to_res, "to_res")
    else:
        reply = await inline.text_buttons_keyboard_resources(call.data, res_list, 0, 5, cb_move_items)
        reply_markup = reply[0]
        res_list = reply[1]

    await bot.edit_message_text(chat_id=call.from_user.id, text=await get_res_desc(call.data, res_list),
                                message_id=call.message.message_id,
                                reply_markup=reply_markup)



@dp.callback_query_handler(cb_move_items.filter())
async def move_items(call: types.CallbackQuery):
    # info = ['0', '5', 'potion', 'next']
    firt_number, last_number, item_type, action = call.data.split(":")[1].split("-")

    user_info = await get_user_info(call.from_user.id)
    res_list = await DB.get_resources(user_info.nickname, item_type)

    first_num = int(firt_number) + 5 if action == "next" else int(firt_number) - 5
    last_num = int(last_number) + 5 if action == "next" else int(last_number) - 5

    reply = await inline.text_buttons_keyboard_resources(item_type, res_list, first_num, last_num, cb_move_items)

    if reply[1]:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=await get_res_desc(item_type, reply[1]),
                                    reply_markup=reply[0])
    # Если список пустой, пишем что последняя или первая страница исходя из action
    else:
        await call.answer(strings.last_page if action == "next" else strings.first_page)



@dp.message_handler(IsPrivate(), text_startswith="/use")
async def potion_use(message: types.Message):
    potion_type = "_".join(message.text.split("_")[1:])

    user_info = await get_user_info(message.from_user.id)

    if await DB.check_item_on_inventory(potion_type, user_info.nickname):
        potion = await DB.get_potion(potion_type)
        asyncio.create_task(potion.use_potion(user_info, potion_type))


    else:
        await bot.send_message(message.from_user.id, strings.you_not_have_need_item)




async def get_res_desc(res_type: str, res_list: list) -> str:
    """
    :param res_type: тип ресурса (potion, recepie, crafter...)
    :param res_list: список этих ресурсов
    :return: описание предмета для меню ресурсов в герое
    """
    if res_type in strings.item_types_res:
        string = f"<b>{strings.item_types_str[res_type]}</b>\n"
        for i in res_list:
            resource = await get_resource(i[1])
            if res_type == "potion":
                string += await resource.potion_description(i[2])
            elif res_type == "recepie":
                string += await resource.crafter_description(i[2])
            else:
                string += await resource.default_description(i[2])

        return string
    else:
        raise TypeError
