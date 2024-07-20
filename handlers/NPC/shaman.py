import asyncio
from random import shuffle

from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.utils import strings, functions
from AzeibarjanWarBOT.utils.class_getter import get_user_info, get_resource
from AzeibarjanWarBOT.filters.filter import IsPrivate

@dp.message_handler(IsPrivate(), text=strings.nps_baki_list[3])
@dp.callback_query_handler(text="boxes_back")
async def shaman_button(message_or_call):
    user_info = await get_user_info(message_or_call.from_user.id)
    if isinstance(message_or_call, types.Message):
        await bot.send_message(message_or_call.from_user.id, strings.shaman_desc.format(await DB.get_count_keys(user_info.nickname)), reply_markup=await inline.boxes_shaman())
    elif isinstance(message_or_call, types.CallbackQuery):
        await bot.edit_message_text(chat_id=message_or_call.from_user.id, message_id=message_or_call.message.message_id, text=strings.shaman_desc.format(await DB.get_count_keys(user_info.nickname)), reply_markup=await inline.boxes_shaman())



@dp.callback_query_handler(text=["siravi_box", "epic_box", "legendary_box"])
async def shaman_callback(call: types.CallbackQuery):
    user_info = await get_user_info(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                text=await functions.get_boxes_description(
                                    call.data,
                                    await DB.get_count_keys(user_info.nickname)),
                                reply_markup=await inline.boxe_actions(call.data))


@dp.callback_query_handler(text_startswith="open_box")
async def open_box(call: types.CallbackQuery):
    box_type = call.data.split("-")[1]
    user_info = await get_user_info(call.from_user.id)
    user_count_keys = await DB.get_count_keys(user_info.nickname)
    box_need_keys = dicts.box_open_cost_value[box_type]

    if box_need_keys > user_count_keys:
        await call.answer(strings.get_you_cant_buy_it.format(user_count_keys), show_alert=True)
    else:
        await DB.delete_from_inventory_with_item_name("nft_key", user_info.nickname, box_need_keys)
        box_loot = await DB.get_box_loot(box_type)
        shuffle(box_loot)
        for loot in box_loot:
            await asyncio.sleep(0.1)

            try:
                current_res = await get_resource(loot[0])
                text = current_res.title
            except TypeError:
                val_spl = loot[0].split(" ")
                current_res = await get_resource(val_spl[0])
                text = f"{current_res.title} - {val_spl[1]}X"

            try:
                await bot.edit_message_text(chat_id=call.from_user.id,
                                            message_id=call.message.message_id,
                                            text=strings.box_is_opening.format(text))

            except MessageNotModified:
                continue

        try:
            last_res = await get_resource(box_loot[-1][0])
            text = last_res.title
            count = None
        except TypeError:
            val_spl = box_loot[-1][0].split(" ")
            last_res = await get_resource(val_spl[0])
            text = f"{last_res.title} - {val_spl[1]}X"
            count = int(val_spl[1])

        if count is not None:
            for i in range(count):
                await DB.add_item_to_inventory(user_info.nickname, last_res.type, last_res.item_id)

        else:
            await DB.add_item_to_inventory(user_info.nickname, last_res.type, last_res.item_id)

        await bot.edit_message_text(chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    text=strings.box_was_opened.format(text),
                                    reply_markup=await inline.box_back())
