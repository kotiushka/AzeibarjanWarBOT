from aiogram import types
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_event, get_user_info, get_resource


@dp.message_handler(IsPrivate(), text=strings.menu_chield_buttons_text[0])
async def event_buttons(message: types.Message):
    try:
        event = await get_event()
        user_info = await get_user_info(message.from_user.id)
        await bot.send_message(message.from_user.id, await event.get_event_description(), reply_markup=await inline.get_event_reward(user_info.event_reward))
    except TypeError:
        await bot.send_message(message.from_user.id, strings.not_have_event)



@dp.callback_query_handler(text="get_event_reward")
async def get_event_reward(call: types.Message):
    user_info = await get_user_info(call.from_user.id)
    if not user_info.event_reward:
        event = await get_event()
        for reward in event.resources.split():
            res_data = reward.split("-")
            current_resource = await get_resource(res_data[0])
            for i in range(int(res_data[1])):
                await DB.add_item_to_inventory(user_info.nickname, current_resource.type, current_resource.item_id)
        await DB.update_balance(event.gold, "+", call.from_user.id)
        await DB.update_balance(event.coupons, "+", call.from_user.id, is_coupon=True)

        await call.answer(strings.event_reward_now_taked)
        await DB.set_event_reward(call.from_user.id, 1)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=await inline.get_event_reward(1))


    else:
        await call.answer(strings.event_reward_been_taked)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message_id, reply_markup=None)




@dp.callback_query_handler(text="event_reward_already_taked")
async def event_reward_already_taked(call: types.CallbackQuery):
    return await call.answer(strings.event_reward_been_taked)