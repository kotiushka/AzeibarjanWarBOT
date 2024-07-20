import asyncio

import aioschedule
from aiogram import types

from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.keyboards import default, inline
from AzeibarjanWarBOT.loader import bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.src.dicts import resources_chield_types
from AzeibarjanWarBOT.src.resource import Resource
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_location, get_trick, get_user_info, get_item, get_resource, get_quest


async def ret_city(user_id):
    user_info = await get_user_info(user_id)
    location = await get_location(user_info.city)

    location = await get_location(location.id)
    is_city = await location.get_is_city

    text = await location.get_text_city(user_info) if is_city is True else await location.get_text_location(user_info)

    await bot.send_photo(user_id, caption=text, photo=types.InputFile(f"utils/images/{location.id}.jpg"),
                         reply_markup=await default.buttons_menu(user_id,
                                                                 city=False if location.id == "coliseum" else is_city,
                                                                 coliseum=location.id == "coliseum"))


async def heal_hp(user_id):
    user_info = await get_user_info(user_id)
    lvl = user_info.lvl
    current_hp = user_info.current_hp
    aviable_haracteristics = await user_info.get_aviable_haracteristics()
    max_hp = aviable_haracteristics[0]
    speed = 1 if lvl < 5 else 0.8
    speed = speed - ((speed * user_info.regen_hp) / 100)

    flag = True if max_hp / 2 >= current_hp else False

    if not user_info.healing:
        if user_info.current_hp != aviable_haracteristics[0]:
            await DB.set_healing(user_id, 1)
            while current_hp < max_hp - 1:

                user_info = await get_user_info(user_id)

                if user_info.healing == 0:
                    return

                aviable_haracteristics = await user_info.get_aviable_haracteristics()
                current_hp = user_info.current_hp
                max_hp = aviable_haracteristics[0]

                if current_hp > max_hp:
                    await DB.set_healing(user_id, 0)
                    return await DB.set_current_hp(user_id, current_hp - max_hp, "-")

                if flag is True and round(max_hp / 2) == current_hp:
                    await bot.send_message(user_id, strings.health_up[0])
                await asyncio.sleep(speed)
                await DB.set_current_hp(user_id)

            await DB.set_healing(user_id, 0)
            await bot.send_message(user_id, strings.health_up[1])


async def buy_item(call: types.CallbackQuery, type, npc_eng, sale=0, is_coupon=False, button_back=False):
    item_id = call.data.split(":")[1]
    if type == "item":
        try:
            current_item = await get_item(item_id)
        except TypeError:
            current_item = await get_resource(item_id)
        action = 0
    else:
        current_item = await get_trick(item_id)
        action = 1

    user_info = await get_user_info(call.from_user.id)

    current_balance = user_info.gold if not is_coupon else user_info.coupon
    cost = int(current_item.cost - ((current_item.cost * sale) / 100))

    if current_balance < cost:
        await call.answer(strings.get_you_cant_buy_it.format(current_balance), True)
    else:
        await add_quest_received(f"gold_{cost}", user_info.id)
        item_type = current_item.type
        await DB.update_balance(cost, "-", call.from_user.id) if not is_coupon else await DB.update_balance(cost, "-",
                                                                                                            call.from_user.id,
                                                                                                            is_coupon=True)
        await DB.add_item_to_inventory(user_info.nickname, item_type, item_id)

        await call.answer(await strings.get_you_buy(current_item.title, action), True)
        # Если тип предмета ресурсный но не указан в базе (может быть свиток-ресурс и тд)
        if item_type in resources_chield_types:
            item_type = "resources"

        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            reply_markup=await inline.dealer_buy_item_only_back(
                                                f"{item_type}_{npc_eng}" if not button_back else button_back))


async def get_name_availability(name):
    if len(name) > 16 or name.isdigit():
        return "not_aviable"

    for char in name.lower():
        if char not in strings.availableSymbols:
            return "not_aviable"

    is_name_busy = await DB.get_busy_name(name)
    return "busy" if is_name_busy else "not busy"


async def increase_player_level(user_info: User, experience_points):
    current_level = user_info.lvl
    current_expiriance = user_info.current_xp
    user_id = user_info.id

    # если игрок находится на максимальном уровне, функция не может повысить его уровень
    if current_level == 'SSS':
        return current_level, current_expiriance

    # определяем количество очков опыта, необходимых для перехода на следующий уровень
    points_needed = config.POINTS_REQUIRED[current_level - 1]

    # если набрано достаточно очков опыта для перехода на следующий уровень
    exp_with_boost = experience_points + current_expiriance
    if exp_with_boost >= points_needed:
        current_level += 1
        # вычисляем оставшиеся очки опыта, которые будут перенесены на следующий уровень
        remaining_experience = exp_with_boost - points_needed

        await DB.change_user_lvl(user_id, current_level, remaining_experience)
        await DB.change_stat_point(user_id, 3, "+")
        await bot.send_message(user_id, strings.get_new_lvl_text.format(current_level))
        aviable_haracteristics = await user_info.get_aviable_haracteristics()
        await DB.set_full_hp(aviable_haracteristics[0], user_info.id)

    else:
        await DB.change_user_lvl(user_id, current_level, exp_with_boost)


async def add_quest_received(quest_type: str, user_id):
    user_quests = await DB.get_quest_user(user_id)
    for quest in user_quests:
        current_quest = await get_quest(quest[0])
        if current_quest.quest_type_req.split("_")[0] == "gold":
            try:
                gold_count = int(quest_type.split("_")[1])
            except ValueError:
                continue
            user_quest_received = await DB.get_quest_user_received(user_id, current_quest.id)

            if gold_count + user_quest_received > current_quest.required:
                gold_count = current_quest.required

            await DB.add_received_quest(user_id, current_quest.id, gold_count)

        else:
            if current_quest.quest_type_req == quest_type:
                await DB.add_received_quest(user_id, current_quest.id)


async def clear_quests(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        await DB.clear_quests()


async def get_lvl_good(user_lvl):
    if str(user_lvl).isdigit():
        if user_lvl == 31:
            return "SS"
        elif user_lvl == 32:
            return "SSS"
        return user_lvl
    else:
        if user_lvl == "SS":
            return 31
        elif user_lvl == "SSS":
            return 32


async def update_clan_wars():
    clan_war_info = await DB.get_clan_war()
    await DB.set_clan_war_active()
    await DB.set_clan_war_next_war()
    if clan_war_info[0] == 1:
        clan_top = await DB.select_top_info('clan_top')  # -> [[2, 84], [3, 27], [3, 45]] ex
        iteration = 1
        for clan in clan_top:
            clan_reward = dicts.clan_war_rewards[iteration]
            clan_users = await DB.select_clan_users(clan[0])  # -> [(3, 5553880543, 2), (., ., .),] ex
            for user in clan_users:
                user_info = await get_user_info(user[1])
                for reward in clan_reward:
                    res_count = clan_reward[reward]

                    if reward != "gold":
                        resource = Resource(*await DB.get_resource(reward))
                        for _ in range(res_count):
                            await DB.add_item_to_inventory(user_info.nickname, resource.type, resource.item_id)
                    else:
                        await DB.update_balance(res_count, "+", user_info.id)

                await bot.send_message(user_info.id, strings.clan_war_rewards[iteration])
            iteration += 1
    else:
        await DB.reset_pvp_points()


async def schedule():
    # Запускаем цикл асинхронных задач
    aioschedule.every(config.CLAN_WAR_DAYS_TIME).days.do(update_clan_wars)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def get_box_loot(loot: list[str]):
    resultat = [strings.box_resources_drop]
    for nft in loot:
        try:
            res = await get_resource(nft[0])
        except TypeError:
            val_spl = nft[0].split(" ")
            res = await get_resource(val_spl[0])
            resultat.append(f"{res.title} - {val_spl[1]}X")
            continue

        resultat.append(res.title)

    return "\n‣ ".join(resultat)


async def get_boxes_description(box, user_count_keys):
    boxes_info = {"siravi_box": ["siravi_box", 'сирави'], "epic_box": ["epic_box", 'эпическая'],
                  "legendary_box": ["legendary_box", 'легендарная']}
    boxes_i = boxes_info[box]

    return f"<b>{dicts.boxes_rarity_list[boxes_i[0]]}</b>\n\n" \
           f"{strings.box_raruty.format(boxes_i[1])}\n\n" \
           f"{await get_box_loot(await DB.get_box_loot(boxes_i[0]))}\n\n" \
           f"{strings.box_open_cost.format(dicts.box_open_cost_value[boxes_i[0]], user_count_keys)}"
