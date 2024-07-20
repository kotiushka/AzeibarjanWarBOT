import asyncio

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.handlers.person.hero import can_use_item, use_item
from AzeibarjanWarBOT.keyboards import default, inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info
from AzeibarjanWarBOT.utils.functions import heal_hp

cb_push = CallbackData("pusher", "point")

@dp.message_handler(IsPrivate(), text=strings.hero_buttots_keyb[4])
async def points(message: types.Message):
    """🧬 Параметры"""
    user_info = await get_user_info(message.from_user.id)
    text = await strings.get_point_desc(user_info.lvl, user_info.get_arr_atr)

    await bot.send_message(message.from_user.id, text, reply_markup=await default.point_buttons())


@dp.message_handler(IsPrivate(), text=strings.point_buttons[0])
async def point_distribute(message: types.Message):
    """🧬 Распределить"""
    user_info = await get_user_info(message.from_user.id)

    text = await strings.get_point_distribute_text(user_info.get_arr_atr)
    # Если очков параметров больше или равно 1
    if user_info.stat_point >= 1:
        # Сообщение с инлайн кнопками, в конце куда распределить
        await bot.send_message(message.from_user.id, text + f"\n\n{strings.where_push_point}", reply_markup=await inline.distribute_points(cb_push, user_info.lvl))
    else:
        # Сообщение что очки кончились
        await bot.send_message(message.from_user.id, strings.points_is_null_2)


@dp.callback_query_handler(cb_push.filter())
async def push_point(call: types.CallbackQuery):
    """Обработка нажатий на кнопки распределения очков"""
    user_info = await get_user_info(call.from_user.id)
    push_type = call.data.split(":")[1]
    # Если очков параметров больше или равно 1
    if user_info.stat_point >= 1:
        # Изменяем все характеристики
        await DB.up_point_skill(call.from_user.id, push_type)
        await DB.change_stat_point(call.from_user.id, 1, "-")

        user_info = await get_user_info(call.from_user.id)
        text = await strings.get_point_distribute_text(user_info.get_arr_atr)

        # Если очков параметров больше или равно 1 (после изменений)
        if user_info.stat_point >= 1:
            # Сообщение с инлайн кнопками, в конце куда хотите распределить
            await bot.edit_message_text(chat_id=call.from_user.id, text=text + f"\n\n{strings.where_push_point}",
                                        message_id=call.message.message_id,
                                        reply_markup=await inline.distribute_points(cb_push, user_info.lvl))
        else:
            # Сообщение без инлайн кнопок распределения, в конце что очки кончились
            await bot.edit_message_text(chat_id=call.from_user.id, text=text + f"\n\n{strings.points_is_null}",
                                        message_id=call.message.message_id)
        # Ответ на нажатие кнопки, было добавлено очко навыка ...
        await call.answer(strings.push_points_dict[push_type])
        # Запускаем отхил хп если вкачали выносливость
        if push_type == "force":
            asyncio.create_task(heal_hp(call.from_user.id))

    # Если очков 0
    else:
        await call.answer(strings.points_is_null)



@dp.message_handler(IsPrivate(), text=strings.point_buttons[1])
async def reset_points(message: types.Message):
    """🔄 Сброс параметров"""
    user_info = await get_user_info(message.from_user.id)
    if await DB.check_item_on_inventory("scroll_reset", user_info.nickname):
        await bot.send_message(message.chat.id, strings.reset_params_have, reply_markup=await inline.get_one_item_keyb(
            strings.reset_params, "reset_params"))
    else:
        await bot.send_message(message.from_user.id, strings.reset_params_no_have, reply_markup=await inline.item_no_have_actions())




@dp.callback_query_handler(text="reset_params")
async def reset_callback(call: types.CallbackQuery):
    """Сброс параметров кнопка"""
    user_info = await get_user_info(call.from_user.id)

    reset = await DB.select_resource("scroll_reset", user_info.nickname)

    if reset:
        await bot.edit_message_text(chat_id=call.from_user.id, text=strings.successfull_reseted, message_id=call.message.message_id)
        await DB.reset_params(call.from_user.id)
        await DB.delete_from_inventory(reset, user_info.nickname)

        asyncio.create_task(heal_hp(call.from_user.id))
        await reset_params_reset_items(call.from_user.id, "item")
        await reset_params_reset_items(call.from_user.id, "trick")

    else:
        await bot.send_message(call.from_user.id, strings.you_not_have_this_item_now)


async def reset_params_reset_items(user_id, item_type: str) -> None:
    user_info = await get_user_info(user_id)
    if item_type in ["item", "trick"]:
        array = user_info.get_user_weap_arr if item_type == "item" else user_info.get_tricks

        slot = 1
        for i in array:
            if i is not None:
                if item_type == "item":
                    item_info = await DB.get_current_item_from_inventory(user_info.nickname, i.split("-")[1])
                    can_use = await can_use_item(item_info[3], user_info, "item")
                    if can_use:
                        await use_item(user_info.id, item_info[3], item_info[-1], "-")
                        await DB.set_item_use(item_info[0], "no")
                        await DB.set_item_use_users(None, item_info[2], user_info.id)
                else:
                    can_use = await can_use_item(i, user_info, "trick")
                    if can_use:
                        await DB.update_trick(user_info.id, slot)
                    slot += 1
    else:
        raise TypeError


