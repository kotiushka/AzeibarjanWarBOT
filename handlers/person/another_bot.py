from aiogram import types
from aiogram.dispatcher.filters import IsReplyFilter

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsNotPrivate
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings, functions
from AzeibarjanWarBOT.utils.class_getter import get_user_info
from AzeibarjanWarBOT.utils.strings import hero_item_list


@dp.message_handler(IsReplyFilter(is_reply=True), IsNotPrivate(), commands="info")
async def info(message: types.Message):
    try:
        user_info = await get_user_info(message.reply_to_message.from_user.id)
    except TypeError:
        return await bot.send_message(message.chat.id, strings.user_not_in_bot)

    text = f"""
{strings.user_profile}

{await user_info.get_href_userURL()} 

{hero_item_list[0]}{user_info.gold}  
{hero_item_list[1]}{user_info.coupon}
{hero_item_list[11]}{await DB.get_count_keys(user_info.nickname)}   
{hero_item_list[2]}{await functions.get_lvl_good(user_info.lvl)}   
{hero_item_list[3]}{user_info.current_xp}/{AzeibarjanWarBOT.config.POINTS_REQUIRED[user_info.lvl - 1]}
{hero_item_list[4]}{user_info.glory} ({await user_info.get_glory_rank()})
<b>{strings.user_power.format(user_info.pvp_points)}</b>
{hero_item_list[6]}{await user_info.get_collection}"""

    await bot.send_message(message.chat.id, text)


