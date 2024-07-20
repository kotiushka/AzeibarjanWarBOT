from aiogram import types

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate, UserInCity
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.src.craft import Craft
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info, get_item


# Реагируем на текст кузнеца
@dp.message_handler(UserInCity(), IsPrivate(), text=[strings.npc_karabah_list[2], strings.npc_gandja_list[2]])
async def bs_menu(message: types.Message):
    b_desc = await get_blacksmith_description(message.from_user.id)
    await bot.send_message(message.from_user.id, b_desc[0] + "\n\n" + b_desc[1],
                           reply_markup=await inline.blacksmith_buttons(b_desc[-1]))


@dp.callback_query_handler(UserInCity(),
                           text_startswith=["kuchiki_protect", "tessai_protect", "kuchiki_weapon", "tessai_weapon",
                                            "kuchiki_products", "tessai_products"])
async def bs_choise_item_type(call: types.CallbackQuery):
    data = call.data.split("_")

    blacksmith_desc = await get_blacksmith_description(call.from_user.id)

    item_type = data[1]

    if item_type == "protect":
        reply_markup = await inline.blacksmith_protect(blacksmith_desc[-1])
    elif item_type == "weapon":
        reply_markup = await inline.blacksmith_buttons_weapon(blacksmith_desc[-1])
    else:
        reply_markup = await inline.blacksmith_buttons_products(blacksmith_desc[-1])

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=await get_blalcksimth_text(blacksmith_desc),
                                reply_markup=reply_markup)


@dp.callback_query_handler(UserInCity(), text=dicts.blacksmits_types)
async def bs_weapon(call: types.CallbackQuery):
    data = call.data.split("_")
    item_type, bs_cur = data[1], data[0]

    user_info = await get_user_info(call.from_user.id)

    blacksmith_desc = await get_blacksmith_description(call.from_user.id)

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=await get_blalcksimth_text(blacksmith_desc),
                                reply_markup=await inline.blacksmith_items(bs_cur, item_type, user_info.city))


@dp.callback_query_handler(UserInCity(), text_startswith="bcraft")
async def craft_item_choised(call: types.CallbackQuery):
    data = call.data.split("-")
    item_id, bs = data[1:]  # wood_sword_1 kuchiki

    current_item = await get_item(item_id)
    user_info = await get_user_info(call.from_user.id)

    current_craft = Craft(*await DB.get_craft(item_id))
    desc = await current_item.get_item_desc(True, user_info, without_cost=True) + await current_craft.get_description(call.from_user.id)

    await bot.edit_message_text(text=desc, chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                reply_markup=await inline.blacksmith_craft_back(bs, item_id, current_item.type))


@dp.callback_query_handler(UserInCity(), text_startswith="create")
async def create_item(call: types.CallbackQuery):
    data = call.data.split("-")
    item_id, bs = data[1:]  # wood_sword_1 kuchiki

    current_craft = Craft(*await DB.get_craft(item_id))
    if await current_craft.check_can_craft(call.from_user.id):
        await current_craft.craft_item(call.from_user.id)
        current_item_res = await get_item(item_id)
        await call.answer(strings.successfull_created.format(current_item_res.title), show_alert=True)

        bs_desc = await get_blacksmith_description(call.from_user.id)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=bs_desc[0] + "\n\n" + bs_desc[1],
                                    reply_markup=await inline.blacksmith_buttons(bs_desc[-1]))

    else:
        await call.answer(strings.you_dont_have_need_resources, show_alert=True)


@dp.callback_query_handler(UserInCity(), text=["kuchiki_main_back", "tessai_main_back"])
async def bs_main_back(call: types.CallbackQuery):
    bs_desc = await get_blacksmith_description(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=bs_desc[0] + "\n\n" + bs_desc[1],
                                reply_markup=await inline.blacksmith_buttons(bs_desc[-1]))


async def get_blalcksimth_text(blacksmith_desc):
    return f"""
{blacksmith_desc[0]}

{strings.what_you_want_to_create}

{blacksmith_desc[2]}"""


async def get_blacksmith_description(user_id):
    user_info = await get_user_info(user_id)
    return strings.blacksmits[user_info.city]
