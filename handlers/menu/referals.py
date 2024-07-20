from aiogram import types
from aiogram.utils.deep_linking import get_start_link

from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info


@dp.message_handler(IsPrivate(), text=strings.menu_chield_buttons_text[3])
async def referals_message(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    await bot.send_message(message.from_user.id, strings.referal_message.format(len(user_info.referals.split())))
    await bot.send_message(message.from_user.id, strings.invite_game_message.format(await get_start_link(message.from_user.id)), disable_web_page_preview=True, reply_markup=await inline.send_ref_message(message.from_user.id))




@dp.message_handler(IsPrivate(), commands="get_reflist")
async def get_reflist(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    message_text = []
    counter = 1
    for referal in user_info.referals.split():
        try:
            referal_info = await get_user_info(int(referal))
            message_text.append(f"{counter}. {await referal_info.get_href_without_hp()}")
            counter += 1
        except (KeyError, TypeError):
            continue

    await bot.send_message(message.from_user.id, strings.freinds_list_not_empty)
    await send_referal_message(message.from_user.id, message_text)



async def send_referal_message(user_id, referals):
    if len(referals) == 0:
        await bot.send_message(user_id, strings.freinds_list_empty)
    else:
        for refer_message in range(0, len(referals), 150):
            current_list = referals[refer_message:refer_message+150]
            await bot.send_message(user_id, "\n".join(current_list))



