from aiogram import types
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT.filters.filter import IsPrivate, UserInCity
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info, get_resource
from AzeibarjanWarBOT.utils.functions import buy_item

cb_item = CallbackData("zefvald", "get_item")
buy_item_cb = CallbackData("alchimic_buy_item", "item")

@dp.message_handler(UserInCity(), IsPrivate(), text=[strings.nps_baki_list[1], strings.npc_karabah_list[1], strings.npc_gandja_list[1]])
async def alchimic_menu(message: types.Message):
    alch_desc = await get_alchimic_description(message.from_user.id)
    await bot.send_message(message.from_user.id, alch_desc[0] + "\n\n" + alch_desc[1],
                           reply_markup=await inline.alchimic_buttons("zefvald"))


# Боевые приемы
@dp.callback_query_handler(text="zefvald_potions")
async def tricks(call: types.CallbackQuery):
    user_info = await get_user_info(call.from_user.id)
    alch_desc = await get_alchimic_description(call.from_user.id)
    text = f"{alch_desc[0]}\n\n{strings.hero_item_list[0]}{user_info.gold}\n\n{alch_desc[2]}"

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                reply_markup=await inline.dynamic_item_sale(
                                    ["heal_1",
                                     "heal_2",
                                     "heal_3",
                                     "heal_4",
                                     "potion_xp_1"],
                                    cb_item, "potion_zefvald", call.from_user.id,
                                    "resource"))

@dp.callback_query_handler(text="potion_zefvald")
async def back(call: types.CallbackQuery):
    alch_desc = await get_alchimic_description(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=alch_desc[0] + "\n\n" + alch_desc[1],
                                reply_markup=await inline.alchimic_buttons("zefvald"))


@dp.callback_query_handler(cb_item.filter())
async def potion_tap(call: types.CallbackQuery):
    item_id = call.data.split(":")[1]
    current_item = await get_resource(item_id)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=await current_item.get_item_description_full(),
                                reply_markup=await inline.buy_item(f"zefvald_potions", buy_item_cb, item_id))


@dp.callback_query_handler(buy_item_cb.filter())
async def potion_buy(call: types.CallbackQuery):
    await buy_item(call, "item", "zefvald")


async def get_alchimic_description(user_id):
    user_info = await get_user_info(user_id)
    return strings.alhimics[user_info.city]

