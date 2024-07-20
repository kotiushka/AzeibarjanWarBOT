import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.state import states
from AzeibarjanWarBOT.state.states import StartState
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info
from AzeibarjanWarBOT.utils.strings import start_NoneRegisterMessage
from AzeibarjanWarBOT.utils.functions import ret_city, get_name_availability
from AzeibarjanWarBOT.keyboards import default, inline
from AzeibarjanWarBOT.filters.filter import IsPrivate


# Команда старт
@dp.message_handler(IsPrivate(), CommandStart())
async def start(message: types.Message):
    if not await DB.user_check(message.from_user.id):
        args = message.get_args()
        if args:
            try:
                main_referal_id = int(args)
                if await DB.check_referal(message.from_user.id, main_referal_id):
                    await DB.add_refelal(main_referal_id, message.from_user.id)
                    user_info = await get_user_info(main_referal_id)
                    await DB.add_item_to_inventory(user_info.nickname, "potion", "regen_1")
                    await DB.add_item_to_inventory(user_info.nickname, "potion", "potion_xp_2")
                    await bot.send_message(main_referal_id, strings.you_have_new_referal)
            except ValueError:
                pass


        await DB.user_add(message.from_user.id, message.from_user.username)
        await bot.send_photo(message.from_user.id, caption=start_NoneRegisterMessage,
                             photo=types.InputFile('utils/images/start.jpg'),
                             reply_markup=await inline.start_game())

    else:
        user_info = await get_user_info(message.from_user.id)

        if user_info.course is None:
            await bot.send_photo(message.from_user.id, caption=start_NoneRegisterMessage,
                                 photo=types.InputFile("utils/images/start.jpg"), reply_markup=await inline.start_game())

        else:
            await ret_city(message.from_user.id)


@dp.callback_query_handler(text="start_game")
async def start(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, strings.start_choose_course_preview,
                           reply_markup=await default.buttons_start_choose_course())
    await StartState.course.set()


@dp.callback_query_handler(text="start_game_complite")
async def start_complite(call: types.CallbackQuery):
    await ret_city(call.from_user.id)


@dp.message_handler(state=states.StartState.name)
async def start_game_state(message: types.Message, state: FSMContext):
    aviable_name = await get_name_availability(message.text)

    if aviable_name == "not busy":
        await state.finish()
        await DB.set_nickname(message.text, message.from_user.id)
        await bot.send_message(message.from_user.id, strings.startRegistrationComplite,
                               reply_markup=await inline.start_compliteReg())

    elif aviable_name == "not_aviable":
        await bot.send_message(message.from_user.id, strings.startYourNameIsInvalid)
    else:
        await bot.send_message(message.from_user.id, strings.startYourNameIsBusy)


# Обработка сообщений с кнопок
@dp.message_handler(state=states.StartState.course)
async def choose_course(message: types.Message, state: FSMContext):
    try:
        await DB.set_course(dicts.course_variants[message.text], message.from_user.id)
        await bot.send_message(message.from_user.id, strings.startHi)
        await state.finish()
        await bot.send_message(message.from_user.id, strings.startWriteName,
                               reply_markup=await default.button_start_send_nickname(message) if message.from_user.username is not None else await default.get_fight_res_button(
                                   strings.choice_name))
        await states.StartState.name.set()

    except KeyError:
        await bot.send_message(message.from_user.id, strings.start_choose_course_preview,
                               reply_markup=await default.buttons_start_choose_course())

    await asyncio.sleep(300)
    user_info = await get_user_info(message.from_user.id)
    if user_info.nickname is None:
        await bot.send_message(message.from_user.id, strings.startWriteNameIfWaiting)
