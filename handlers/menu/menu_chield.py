from aiogram import types

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import default, inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.state import states
from AzeibarjanWarBOT.state.states import DeleteHero
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info, get_resource


@dp.message_handler(IsPrivate(), text=[strings.menuMainButtonsList[5], strings.settings_buttons_text[3]])
async def menu_ch_main(message: types.Message):
    """📟 Меню"""
    await bot.send_message(message.from_user.id, strings.menu_chield_message,
                           reply_markup=await default.menu_chield_buttons())


@dp.message_handler(IsPrivate(), text=strings.menu_chield_buttons_text[5])
async def settings(message: types.Message):
    """⚙  Настройки"""
    user_info = await get_user_info(message.from_user.id)
    await bot.send_message(message.chat.id,
                           await strings.get_setting_message(user_info.nickname, user_info.course),
                           reply_markup=await default.settings_buttons())


@dp.message_handler(IsPrivate(), text=strings.settings_buttons_text[0])
async def del_hero(message: types.Message):
    """🗑 Удалить персонажа"""
    await bot.send_message(message.from_user.id, strings.delete_hero_message, reply_markup=await default.get_fight_res_button(
        strings.cancel_del))
    await DeleteHero.delete_hero.set()


@dp.message_handler(IsPrivate(), text=strings.settings_buttons_text[1:3])
async def change_nickname_or_course(message: types.Message):
    """🆔 Сменить имя, 👼 Сменить расу"""
    user_info = await get_user_info(message.from_user.id)

    callback = "reset_nickname" if message.text == strings.settings_buttons_text[1] else "reset_course"

    resource = await get_resource(callback)
    text = f"<b>{message.text}</b>\n\n"
    if await DB.check_item_on_inventory(callback, user_info.nickname):
        text += strings.you_have_need_item
        reply_markup = await inline.get_one_item_keyb(strings.reset_name_button, callback)

    else:
        text += f"{strings.not_have_need_item} {resource.title}"
        reply_markup = await inline.item_no_have_actions()

    await bot.send_message(message.chat.id, text, reply_markup=reply_markup)


@dp.callback_query_handler(text=["reset_nickname", "reset_course"])
async def reset_nickname_b(call: types.CallbackQuery):
    user_info = await get_user_info(call.from_user.id)
    if await DB.check_item_on_inventory(call.data, user_info.nickname):

        if call.data == "reset_nickname":
            await states.ChangeStatistic.change_name.set()
            await bot.send_message(call.from_user.id, strings.send_new_nickname,
                                   reply_markup=await default.get_fight_res_button(strings.cancel_del))
        else:
            keyboard = await default.buttons_start_choose_course()
            await bot.send_message(call.from_user.id, strings.start_choose_course_preview,
                                   reply_markup=keyboard.add(strings.cancel_del))

            await states.ChangeStatistic.change_course.set()

    else:
        await bot.edit_message_text(chat_id=call.from_user.id, text=strings.not_have_need_item[:-1],
                                    message_id=call.message.message_id)

@dp.message_handler(IsPrivate(), text=strings.menuMainButtonsList[7])
async def help(message: types.Message):
    """❓ Помощь"""
    await bot.send_message(message.from_user.id, text=strings.info_help_text, reply_markup=await default.help_message_buttons(), disable_web_page_preview=True)


@dp.message_handler(IsPrivate(), text=strings.help_message_buttons[1])
async def data_help(message: types.Message):
    """🗂 База знаний"""
    await bot.send_message(message.from_user.id, text=strings.data_help_message, reply_markup=await inline.data_info_help())


@dp.message_handler(IsPrivate(), text=strings.help_message_buttons[2])
async def guides(message: types.Message):
    """📚 Гайды"""
    await bot.send_message(message.from_user.id, strings.guide_message, disable_web_page_preview=True)


@dp.message_handler(IsPrivate(), text=strings.help_message_buttons[4])
async def rulse(message: types.Message):
    """⚠️ Правила"""
    await bot.send_message(message.from_user.id, strings.rules_message, disable_web_page_preview=True)



@dp.message_handler(IsPrivate(), text=strings.help_message_buttons[3])
async def rulse(message: types.Message):
    """📭 Связь"""
    await bot.send_message(message.from_user.id, strings.support_text, disable_web_page_preview=True)









