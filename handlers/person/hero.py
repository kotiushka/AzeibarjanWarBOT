import asyncio

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.keyboards.default import hero_menu
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings, functions
from AzeibarjanWarBOT.utils.class_getter import get_trick, get_user_info, get_item
from AzeibarjanWarBOT.utils.functions import heal_hp, add_quest_received
from AzeibarjanWarBOT.utils.strings import menuMainButtonsList, hero_buttots_keyb, hero_item_list, \
    hero_information_title, use_weapon, item_types, last_page, first_page, you_cant_use, \
    you_successfully_use_it, you_want_to_up_it, item_actions_inventory, trainer_button_list

item_selected = CallbackData("hero", "select")
# Для кнопок перемещения
cb_1 = CallbackData("add", "adding")
cb_2 = CallbackData("remove", "removing")
cb_item = CallbackData("item", "item_tap")

item_actions = CallbackData("item_tap_more", "back_use_up")
cb_item_upper = CallbackData("item_up", "tap")


@dp.message_handler(IsPrivate(), text=[menuMainButtonsList[2], hero_buttots_keyb[0], trainer_button_list[4]])
async def hero_info(message: types.Message):
    user_info = await get_user_info(message.from_user.id)

    # TODO: изменить когда будут ордены и коллекции
    text = f"""{await user_info.get_href_userURL()} 
   
{hero_item_list[0]}{user_info.gold}  
{hero_item_list[1]}{user_info.coupon}
{hero_item_list[11]}{await DB.get_count_keys(user_info.nickname)}   
{hero_item_list[2]}{await functions.get_lvl_good(user_info.lvl)}   
{hero_item_list[3]}{user_info.current_xp}/{AzeibarjanWarBOT.config.POINTS_REQUIRED[user_info.lvl - 1]}
{hero_item_list[4]}{user_info.glory} ({await user_info.get_glory_rank()})
<b>{strings.user_power.format(user_info.pvp_points)}</b>
{hero_item_list[6]}{await user_info.get_collection}
   
{hero_item_list[7]}{user_info.stat_point}   

{hero_item_list[8]}{user_info.bonus_xp}%
{hero_item_list[9]}{user_info.bonus_gold}%
{hero_item_list[10]}{user_info.regen_hp}%
"""
    await bot.send_message(message.from_user.id, text, reply_markup=await hero_menu())


@dp.message_handler(IsPrivate(), text=hero_buttots_keyb[1])
async def hero_haracteristiks(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    haracteristics = await user_info.get_aviable_haracteristics()
    text = f"""{hero_information_title[0]}
        
{await user_info.get_href_userURL()}

{hero_information_title[1]}{user_info.current_hp}
{hero_information_title[2]}{haracteristics[1]}
{hero_information_title[3]}{user_info.protection}
{hero_information_title[4]}{haracteristics[2]}
{hero_information_title[10]}{haracteristics[3]}


{hero_information_title[5]}
{hero_information_title[6]}{user_info.force}
{hero_information_title[7]}{user_info.power}
{hero_information_title[8]}{user_info.dexterity}
{hero_information_title[9]}{user_info.intuition}

"""
    await bot.send_message(message.from_user.id, text)


@dp.message_handler(IsPrivate(), text=hero_buttots_keyb[2])
async def hero_haracteristiks(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    await bot.send_message(message.from_user.id, await get_hero_desc(message),
                           reply_markup=await inline.get_items_on_inventory(user_info.nickname,
                                                                            item_selected))


# Человек выбрал экипировку
@dp.callback_query_handler(item_selected.filter())
async def item_select(call: types.CallbackQuery):
    user_info = await get_user_info(call.from_user.id)
    array = await DB.get_current_items(user_info.nickname, call.data.split(":")[1])
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=await inline.list_keyboard(array, 0, 5, cb_1, cb_2, cb_item))


# Кнопка вперед в списке предметов
@dp.callback_query_handler(cb_1.filter())
async def nextButtons(call: types.CallbackQuery):
    data = call.data.split(":")[1]
    first_num = int(data.split("-")[0])
    last_num = int(data.split("-")[1])
    list_name = data.split("-")[2]

    user_info = await get_user_info(call.from_user.id)
    nickname = user_info.nickname

    array = await DB.get_current_items(nickname, list_name)

    for i in range(5, 1, -1):
        if not i + first_num > len(array) and i + first_num != len(array):
            await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                reply_markup=await inline.list_keyboard(array, first_num + i,
                                                                                        last_num + 5,
                                                                                        cb_1, cb_2, cb_item))
            return
        else:
            await call.answer(last_page)
            return


# Кнопка назад в списке предметов
@dp.callback_query_handler(cb_2.filter())
async def previoslyButtons(call: types.CallbackQuery):
    data = call.data.split(":")[1]
    first_num = int(data.split("-")[0])
    last_num = int(data.split("-")[1])
    list_name = data.split("-")[2]

    user_info = await get_user_info(call.from_user.id)
    nickname = user_info.nickname

    array = await DB.get_current_items(nickname, list_name)

    if last_num - 5 > 0:
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            reply_markup=await inline.list_keyboard(array, first_num - 5, last_num - 5,
                                                                                    cb_1,
                                                                                    cb_2, cb_item))
    else:
        await call.answer(first_page)


# Обработка нажатия на предмет в списке предметов
@dp.callback_query_handler(cb_item.filter())
async def item_tap(call: types.CallbackQuery):
    item_info = call.data.split(":")[1].split("-")

    item, item_id, item_type, fist_num, last_num = item_info[:]

    item_up_lvl = await DB.get_item_use(item_info[1])
    item_up_lvl = item_up_lvl[1]

    current_item = await get_item(item)

    text = await current_item.get_item_desc(True, await get_user_info(call.from_user.id), item_up_lvl)

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                reply_markup=await inline.item_selected_keyboard(item_id, item, item_type, fist_num,
                                                                                 last_num, item_actions))


@dp.callback_query_handler(item_actions.filter())  # ['5', 'emerald_axe_1', 'axe', 'on']
async def item_actions_handler(call: types.CallbackQuery):
    # Получаем информацию об предмете и об пользователе
    item_info = call.data.split(":")[1].split("-")
    user_info = await get_user_info(call.from_user.id)

    # Получаем информацию с инвентаря, вещь которую выбрал пользователь в таком формате: (11, 'kotyghl', 'sword', 'wood_sword_1', 'no', 0)
    curent_item = await DB.get_current_item_from_inventory(user_info.nickname, item_info[0])

    item = await get_item(curent_item[3])
    array = await DB.get_current_items(user_info.nickname, curent_item[2])

    # Если нажал кнопку Надеть
    if item_info[-1] == "on":
        # Проверка, может ли пользователь надеть вещь, в противном случае сообщаем
        result = await can_use_item(item_info[1], user_info, item)
        if result:
            await call.answer(result, show_alert=True)
        # Если пользователь может надеть вещь
        else:
            # Проверяем, надет ли предмет этого типа на пользователе
            item_use_bool = await DB.get_use_item_bool(call.from_user.id, item_info[2])
            if not item_use_bool[0]:
                await item_put_on_inventory(call, curent_item)
                await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                    reply_markup=await inline.list_keyboard(array, 0, 5, cb_1, cb_2,
                                                                                            cb_item))
                await call.answer(you_successfully_use_it[0] + item.title)

            # Если предмет надет
            else:
                # Снимаем предмет
                used_item = await DB.get_use_item_bool(call.from_user.id, item_info[2])
                used_item = used_item[1]
                used_item = used_item.split("-")[1]
                used_item = await DB.get_current_item_from_inventory(user_info.nickname, int(used_item))
                await DB.set_item_use(used_item[0], "no")
                await use_item(call.from_user.id, used_item[3], used_item[-1], "-")

                # Надеваем предмет
                await item_put_on_inventory(call, curent_item)
                await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                    reply_markup=await inline.list_keyboard(array, 0, 5, cb_1, cb_2,
                                                                                            cb_item))
                await call.answer(you_successfully_use_it[0] + item.title)

    # Если пользователь нажал снять вещь
    elif item_info[-1] == "off":
        await item_remove_from_inventory(call, curent_item)
        await call.answer(you_successfully_use_it[1] + item.title)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            reply_markup=await inline.list_keyboard(array, 0, 5, cb_1, cb_2,
                                                                                    cb_item))
    elif item_info[-1] == "up":
        text = await you_want_to_up_it(item.title)
        await bot.send_message(call.from_user.id, text[0],
                               reply_markup=await inline.upper_keyboard(cb_item_upper, curent_item))


    else:
        array = await DB.get_current_items(user_info.nickname, item_info[2])

        await bot.edit_message_text(text=await get_hero_desc(call), chat_id=call.from_user.id,
                                    message_id=call.message.message_id,
                                    reply_markup=await inline.list_keyboard(array, int(item_info[3]),
                                                                            int(item_info[4]), cb_1,
                                                                            cb_2, cb_item))


@dp.callback_query_handler(cb_item_upper.filter())
async def item_upper_keyb(call: types.CallbackQuery):
    if call.data[8:] != "no":
        user_info = await get_user_info(call.from_user.id)

        shahid = await DB.select_resource("shahid_blood", user_info.nickname)
        if shahid is not None:
            await DB.delete_from_inventory(shahid, user_info.nickname)
            item_haracteristics = call.data.split(":")[1].split("-")
            current_item = [int(item_haracteristics[0]), "", item_haracteristics[1], item_haracteristics[2],
                            item_haracteristics[3], int(item_haracteristics[4])]

            current = await get_item(current_item[3])
            text = await you_want_to_up_it(current.title)
            text = text[1]

            if current_item[4] == "yes":
                await add_quest_received("up_equip", call.from_user.id)
                await item_remove_from_inventory(call, current_item)
                current_item[5] += 1
                await DB.up_item_lvl(current_item[0], current_item[5])
                await item_put_on_inventory(call, current_item)

                await bot.edit_message_text(text, chat_id=call.from_user.id, message_id=call.message.message_id)
            else:
                current_item[5] += 1
                await DB.up_item_lvl(current_item[0], current_item[5])
                await bot.edit_message_text(text, chat_id=call.from_user.id, message_id=call.message.message_id)
        else:
            await bot.edit_message_text(item_actions_inventory[-1], chat_id=call.from_user.id,
                                        message_id=call.message.message_id)
    else:
        await call.message.delete()


@dp.callback_query_handler(text="back_hero")
async def hero_back_keyb(call: types.CallbackQuery):
    user_info = await get_user_info(call.from_user.id)
    nickname = user_info.nickname

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=await get_hero_desc(call),
                                reply_markup=await inline.get_items_on_inventory(nickname,
                                                                                 item_selected))


# Кнопка "Экипировка"
async def get_hero_desc(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    use_items = await DB.get_use_items_from_inventory(user_info.nickname)

    text = await user_info.get_href_userURL() + "\n\n" + use_weapon + "\n\n"
    for i in range(9):
        text += item_types[i]
        if use_items[i] is None:
            text += "-\n"
        else:
            use_item_id = use_items[i].split('-')
            use_item_up = await DB.get_item_use(int(use_item_id[1]))
            use_item_up = use_item_up[1]
            use_item_up = "" if str(use_item_up) == "0" else f" (+{use_item_up})"
            current_item = await get_item(use_item_id[0])
            text += f"<i>{current_item.title}</i> {use_item_up}" + "\n"
    return text


async def item_remove_from_inventory(call: types.CallbackQuery, curent_item):
    # current_item = (19, 'kotyghl', 'axe', 'wood_axe_1', 'yes', 0)
    await use_item(call.from_user.id, curent_item[3], curent_item[-1], "-")
    asyncio.create_task(heal_hp(call.from_user.id))
    await DB.set_item_use(curent_item[0], "no")
    await DB.set_item_use_users(None, curent_item[2], call.from_user.id)

async def item_put_on_inventory(call: types.CallbackQuery, current_item):
    await use_item(call.from_user.id, current_item[3], current_item[-1])
    await DB.set_item_use_users(f"{current_item[3]}-{current_item[0]}", current_item[2], call.from_user.id)
    asyncio.create_task(heal_hp(call.from_user.id))
    await DB.set_item_use(current_item[0], "yes")


async def use_item(user_id, item, up_lvl, operand="+"):
    """Принимает юзерайди, название предмета, уровень заточки, операция: - или +
    Изменяет характеристики персонажа исходя из предмета и уровня заточки"""
    current_item = await get_item(item)
    for bonuses in current_item.get_item_bonuses:
        if bonuses[1] != 0:
            await DB.use_item_upper(user_id, bonuses[0], bonuses[1] + up_lvl, operand)

    return True


async def can_use_item(item_id, user_info, type):
    """Функция проверки может ли использовать юзер предмет,
    в противном случае возвращает текст с необходимыми параметрами."""
    item_info = await get_item(item_id) if type != "trick" else await get_trick(item_id)

    requirements = []

    item_info.need_lvl = await functions.get_lvl_good(item_info.need_lvl)

    if item_info.need_lvl > user_info.lvl:
        requirements.append(you_cant_use[0])
    if item_info.need_power > user_info.power:
        requirements.append(you_cant_use[1])
    if item_info.need_force > user_info.force:
        requirements.append(you_cant_use[2])
    if item_info.need_intuition > user_info.intuition:
        requirements.append(you_cant_use[3])
    if item_info.need_dexterity > user_info.dexterity:
        requirements.append(you_cant_use[4])

    if requirements:
        message_cant_use = you_cant_use[6] if type == "trick" else you_cant_use[5]
        return message_cant_use + "\n".join(requirements)

    else:
        return None




