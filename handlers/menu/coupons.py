from aiogram import types
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import default, inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_resource, get_user_info
from AzeibarjanWarBOT.utils.functions import buy_item, add_quest_received

cb_item_tap = CallbackData("res", "tap")
cb_item_buy = CallbackData("buy_res", "res_buy")

@dp.message_handler(IsPrivate(), text=strings.menu_chield_buttons_text[1])
async def coupons(message: types.Message):
    """Купоны"""
    await bot.send_message(message.from_user.id, strings.coupons_message, reply_markup=await default.coupon_buttons())

@dp.message_handler(IsPrivate(), text=strings.coupons_buttons[1])
async def add_coupons(message: types.Message):
    """Пополнить"""
    await bot.send_message(message.from_user.id, strings.shop_message.format(message.text), reply_markup=await inline.add_coupons_message())


@dp.callback_query_handler(text="back_to_shop_c")
@dp.message_handler(IsPrivate(), text=strings.coupons_buttons[0])
async def coupon_shop(message_or_call):
    """🎫 Магазин"""
    if isinstance(message_or_call, types.Message):
        return await bot.send_message(message_or_call.from_user.id, strings.shop_message.format(
            strings.coupons_buttons[0]), reply_markup=await inline.shop_coupons_message())
    return await bot.edit_message_text(chat_id=message_or_call.from_user.id,
                                       text=strings.shop_message.format(strings.coupons_buttons[0]),
                                       reply_markup=await inline.shop_coupons_message(),
                                       message_id=message_or_call.message.message_id)


@dp.callback_query_handler(text=['c_premium', 'c_regeneration', 'c_gold', 'c_keys', 'c_other', "c_xp"])
async def choice_category(call: types.CallbackQuery):
    reply_markup = await inline.dynamic_item_sale(dicts.coupon_shop_values[call.data],
                                                  cb=cb_item_tap, button_return="back_to_shop_c",
                                                  user_id=call.from_user.id, type="resource", is_coupon=True)

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=strings.coupons_titles[call.data],
                                reply_markup=reply_markup)


@dp.callback_query_handler(cb_item_tap.filter())
async def item(call: types.CallbackQuery):
    item_id = call.data.split(":")[1]
    current_item = await get_resource(item_id)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=await current_item.get_item_description_full(symbol="🎫"), reply_markup=await inline.buy_item(f"back_to_shop_c", cb_item_buy, item_id, symbol="🎫"))


@dp.callback_query_handler(cb_item_buy.filter())
async def buy(call: types.CallbackQuery):
    await buy_item(call, "item", "c", button_back="back_to_shop_c", is_coupon=True)


@dp.message_handler(IsPrivate(), commands=["openbag_1", "openbag_2", "openbag_3"])
async def openbag(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    bag_id = int(message.text.split("_")[1])
    bag_name = f'openbag_{bag_id}'

    bag = await DB.select_resource(bag_name, user_info.nickname)
    if bag is not None:
        await add_quest_received("open_gold_bag", message.from_user.id)
        bag_res = dicts.bags_result[bag_id]
        await DB.delete_from_inventory_with_item_name(bag_name, user_info.nickname)
        await DB.update_balance(bag_res, "+", message.from_user.id)
        await bot.send_message(message.from_user.id, strings.successfully_used_bag.format(bag_res))
    else:
        await bot.send_message(message.from_user.id, strings.not_have_need_item, reply_markup=await inline.item_no_have_actions())



