from aiogram import types
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate, UserInCity
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info, get_item, get_resource
from AzeibarjanWarBOT.utils.functions import buy_item

item_filter = CallbackData("centur", "get_item")
filter_buy = CallbackData("cent", "buy_item")


# Реагируем на текст торговца
@dp.message_handler(UserInCity(), IsPrivate(),
                    text=[strings.nps_baki_list[0], strings.npc_karabah_list[0], strings.npc_gandja_list[0]])
async def centur_menu(message: types.Message):
    dealer_desc = await get_dealers_description(message.from_user.id)
    await bot.send_message(message.from_user.id, dealer_desc[0] + "\n\n" + dealer_desc[1],
                           reply_markup=await inline.dealer_buttons(dealer_desc[-1]))


# Кнопка оружие, броня, изделия, ресурсы
@dp.callback_query_handler(text_startswith=["weapon", "protect", "products"])
async def centur_weapon(call: types.CallbackQuery):
    dealer_desc = await get_dealers_description(call.from_user.id)
    cd = call.data.split("_")[0]
    reply_markup = None
    if cd == "weapon":
        reply_markup = await inline.dealer_buttons_weapon(dealer_desc[-1])
    elif cd == "protect":
        reply_markup = await inline.dealer_buttons_protect(dealer_desc[-1])
    elif cd == "products":
        reply_markup = await inline.dealer_buttons_products(dealer_desc[-1])

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=await get_dealer_text(call.from_user.id, dealer_desc),
                                reply_markup=reply_markup)


# Кнопка назад
@dp.callback_query_handler(text_startswith=["back_c", "back_m", "back_n"])
async def back_weapon(call: types.CallbackQuery):
    dealer_desc = await get_dealers_description(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=dealer_desc[0] + "\n\n" + dealer_desc[1],
                                reply_markup=await inline.dealer_buttons(dealer_desc[-1]))


# Реагируем на одну из кнопок продаж.
@dp.callback_query_handler(text_startswith=["sword", "axe", "dagger", "helmet", "armor", "shield",
                                 "gloves", "boots", "necklace", "ring", "resources"])
async def sword_weapon(call: types.CallbackQuery):
    dealer_desc = await get_dealers_description(call.from_user.id)

    item_type = call.data.split("_")[0]
    items = await DB.get_dealer_items(item_type, dealer_desc[-1])


    type = "resource" if call.data.split("_")[0] == "resources" else "item"

    reply_markup = await inline.dynamic_item_sale(items,
                                                  cb=item_filter, button_return=f"back_{dealer_desc[-1]}",
                                                  user_id=call.from_user.id, type=type)

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=await get_dealer_text(call.from_user.id, dealer_desc),
                                reply_markup=reply_markup)


# Получаем информацию о выбранном оружии, кнопки продать и назад
@dp.callback_query_handler(item_filter.filter())
async def item(call: types.CallbackQuery):
    dealer_desc = await get_dealers_description(call.from_user.id)

    item_id = call.data.split(":")[1]
    try:
        current_item = await get_item(item_id)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=await current_item.get_item_desc(current_item.type != "resources",
                                                                          await get_user_info(call.from_user.id)),
                                    reply_markup=await inline.buy_item(f"{current_item.type}_{dealer_desc[-1]}", filter_buy, item_id))
    except TypeError:
        current_item = await get_resource(item_id)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=await current_item.get_item_description_full(), reply_markup=await inline.buy_item(f"resources_{dealer_desc[-1]}", filter_buy, item_id))



@dp.callback_query_handler(UserInCity(), filter_buy.filter())
async def buy(call: types.CallbackQuery):
    dealer_desc = await get_dealers_description(call.from_user.id)

    await buy_item(call, "item", dealer_desc[-1])


# Общий текст с кол-вом монет
async def get_dealer_text(user_id, dealer_desc):
    user_info = await get_user_info(user_id)
    return f"""
{dealer_desc[0]}

{strings.hero_item_list[0]}{user_info.gold}

{dealer_desc[2]}"""


async def get_dealers_description(user_id):
    user_info = await get_user_info(user_id)
    return strings.dealers[user_info.city]
