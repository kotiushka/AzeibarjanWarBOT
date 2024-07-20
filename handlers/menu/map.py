import asyncio
from random import randint

from aiogram import types
from aiogram.dispatcher import FSMContext

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import default
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.state.states import MapState
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_location, get_user_info
from AzeibarjanWarBOT.utils.functions import ret_city


# Кнопка Карта
@dp.message_handler(IsPrivate(), text=strings.menuMainButtonsList[0])
async def map_main(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    location = await get_location(user_info.city)
    await bot.send_photo(message.from_user.id, photo=types.InputFile('utils/images/map.jpg'),
                         caption=strings.map_description,
                         reply_markup=await default.get_keyboard_nested(await dicts.get_transitions(location.aviable_locations.split())))


@dp.message_handler(IsPrivate(), text=[*strings.transitions_names])
async def go_transition(message: types.Message, state: FSMContext):
    user_info = await get_user_info(message.from_user.id)
    current_location = await get_location(user_info.city)

    need_location = await DB.get_location_id(message.text)
    need_location = await get_location(need_location)

    # Проверка, есть ли неообходимый уровень у человека
    if need_location.id in current_location.aviable_locations:
        location_need_lvl = need_location.need_lvl
        # Если уровень подходит
        if not location_need_lvl > user_info.lvl:
            wait_time = randint(10, 40)
            await bot.send_message(message.from_user.id, strings.transit_action.format(need_location.name, wait_time),
                                   reply_markup=await default.cancel_button())

            await MapState.cancel_go.set()
            asyncio.create_task(ttl_state(state, wait_time, message.from_user.id, need_location.id))


        # Если уровень не подходит
        else:
            await bot.send_message(message.from_user.id, strings.you_cant_transit.format(location_need_lvl))


async def ttl_state(state: FSMContext, sleep_time, user_id, location_id):
    await asyncio.sleep(sleep_time)
    if await state.get_state():
        await DB.set_city(user_id, location_id)
        await ret_city(user_id)
    await state.finish()



@dp.message_handler(IsPrivate(), state=MapState.cancel_go)
async def cancel_transition(message: types.Message, state: FSMContext):
    if message.text == strings.cancel_transition:
        await state.finish()
        await ret_city(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, strings.you_in_transit)