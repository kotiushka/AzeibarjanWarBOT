from aiogram import types
from aiogram.dispatcher import FSMContext

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import default, inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.state.states import DeleteHero, ChangeStatistic
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info
from AzeibarjanWarBOT.utils.functions import ret_city, get_name_availability


@dp.message_handler(IsPrivate(), state=DeleteHero.delete_hero)
async def delete_hero(message: types.Message, state: FSMContext):
    await state.finish()
    # Если текст == УДАЛИТЬ ПЕРСОНАЖА
    if message.text == strings.delete_hero:

        user_info = await get_user_info(message.from_user.id)
        user_clan_info = await DB.get_clan_user(message.from_user.id)

        if user_clan_info is None or (user_clan_info is not None and user_clan_info[2] != 2):
            # Удаляем всю инфу об персонаже
            await DB.delete_all_info_about_person(user_info.id, user_info.nickname)
            # удаляем reply_markup для сообщения
            await bot.send_message(message.from_user.id, strings.successfull_input_del_hero, reply_markup=None)
            # Начинаем регистрацию
            await DB.user_add(message.from_user.id, message.from_user.username)
            await bot.send_photo(message.from_user.id, caption=strings.start_NoneRegisterMessage,
                                 photo=types.InputFile("utils/images/start.jpg"), reply_markup=await inline.start_game())
        else:
            await bot.send_message(message.from_user.id, strings.you_cant_delete_person)
            await ret_city(message.from_user.id)

    else:
        # Если текст == отменить
        if message.text == strings.cancel_del:
            text = strings.canceled_del_hero
        # Если текст не подходит под любые условия
        else:
            text = strings.not_successfull_input_del_hero

        await bot.send_message(message.from_user.id, text)
        await ret_city(message.from_user.id)




@dp.message_handler(IsPrivate(), state=ChangeStatistic.change_name)
async def change_name(message: types.Message, state: FSMContext):
    if message.text != strings.cancel_del:
        name_aviablity = await get_name_availability(message.text)

        if name_aviablity == "not busy":
            await state.finish()
            user_info = await get_user_info(message.from_user.id)

            reset = await DB.select_resource("reset_nickname", user_info.nickname)
            await DB.delete_from_inventory(reset, user_info.nickname)

            await DB.change_nickname_person(message.from_user.id, user_info.nickname, message.text)

            await bot.send_message(message.from_user.id, strings.name_changed)
            await ret_city(message.from_user.id)

        elif name_aviablity == "not_aviable":
            await bot.send_message(message.from_user.id, strings.startYourNameIsInvalid)
        else:
            await bot.send_message(message.from_user.id, strings.startYourNameIsBusy)
    else:
        await state.finish()
        await bot.send_message(message.from_user.id, strings.action_canceled)
        await ret_city(message.from_user.id)




# Обработка сообщений с кнопок выбора рассы
@dp.message_handler(state=ChangeStatistic.change_course)
async def choose_course(message: types.Message, state: FSMContext):
    try:
        await DB.set_course(dicts.course_variants[message.text], message.from_user.id)
        await state.finish()

        user_info = await get_user_info(message.from_user.id)

        reset = await DB.select_resource("reset_course", user_info.nickname)
        await DB.delete_from_inventory(reset, user_info.nickname)

        await bot.send_message(message.from_user.id, strings.course_changed)
        await ret_city(message.from_user.id)

    except KeyError:
        if message.text == strings.cancel_del:
            await state.finish()
            await bot.send_message(message.from_user.id, strings.action_canceled)
            await ret_city(message.from_user.id)
        else:
            await bot.send_message(message.from_user.id, strings.start_choose_course_preview,
                                   reply_markup=await default.buttons_start_choose_course())


