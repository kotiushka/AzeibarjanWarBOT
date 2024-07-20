from aiogram import types

from AzeibarjanWarBOT.keyboards.default import npc_menu
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info
from AzeibarjanWarBOT.utils.functions import ret_city
from AzeibarjanWarBOT.filters.filter import IsPrivate, UserInCity


@dp.message_handler(UserInCity(), IsPrivate(), text=strings.menuMainButtonsList[1])
async def npc(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    await bot.send_photo(message.from_user.id, caption=strings.city_desc, photo=types.InputFile("utils/images/city.jpg", "rb"), reply_markup=await npc_menu(user_info.city))


@dp.message_handler(IsPrivate(), text=[strings.nps_baki_list[-1], strings.to_location, strings.hero_buttots_keyb[-1]])
async def npc_back(message: types.Message):
    await ret_city(message.from_user.id)




