from aiogram import types
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_trick, get_user_info
from AzeibarjanWarBOT.utils.functions import buy_item

cb_item = CallbackData("ael", "get_item")
cb_buy = CallbackData("ael_b", "buy")


# Реагируем на текст тренера
@dp.message_handler(IsPrivate(), text=[strings.nps_baki_list[2], strings.npc_karabah_list[3], strings.npc_gandja_list[3]])
async def ael_menu(message: types.Message):
    trainer_desc = await get_trainer_description(message.from_user.id)
    await bot.send_message(message.from_user.id, trainer_desc[0] + "\n\n" + trainer_desc[1],
                           reply_markup=await inline.trainer_buttons(trainer_desc[-1]))


# Боевые приемы
@dp.callback_query_handler(text_startswith=["trick_a", "trick_u"])
async def tricks(call: types.CallbackQuery):
    trainer_desc = await get_trainer_description(call.from_user.id)
    user_info = await get_user_info(call.from_user.id)
    text = f"{trainer_desc[0]}\n\n{trainer_desc[0]}{user_info.gold}\n\n{trainer_desc[2]}"

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                reply_markup=await inline.dynamic_item_sale(dicts.trainers_trick_list[trainer_desc[-1]],
                                                                            cb_item, "trick_back", call.from_user.id, "trick"))


# Назад (Боевые приемы)
@dp.callback_query_handler(text="trick_back")
async def back(call: types.CallbackQuery):
    trainer_desc = await get_trainer_description(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=trainer_desc[0] + "\n\n" + trainer_desc[1],
                                reply_markup=await inline.trainer_buttons(trainer_desc[-1]))


@dp.callback_query_handler(cb_item.filter())
async def trick_tap(call: types.CallbackQuery):
    trainer_desc = await get_trainer_description(call.from_user.id)

    trick = await get_trick(call.data.split(":")[1])
    user_info = await get_user_info(call.from_user.id)

    if not await DB.check_item_on_inventory(trick.id, user_info.nickname):
        reply_markup = await inline.buy_item(f"trick_{trainer_desc[-1]}", cb_buy, trick.id, 1)
    else:
        reply_markup = await inline.dealer_buy_item_only_back(f"trick_{trainer_desc[-1]}")

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=await trick.get_item_desc_dealer(user_info, trainer_desc[0]),
                                reply_markup=reply_markup)


@dp.callback_query_handler(cb_buy.filter())
async def trick_buy(call: types.CallbackQuery):
    await buy_item(call, "tricks", "ael")


async def get_trainer_description(user_id):
    user_info = await get_user_info(user_id)
    return strings.trainers[user_info.city]
