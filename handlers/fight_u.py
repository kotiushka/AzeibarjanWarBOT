import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import default
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src.fight_room_u import FightRoomUsers
from AzeibarjanWarBOT.state.states import FightState, FightStateUser
from AzeibarjanWarBOT.utils import strings, functions
from AzeibarjanWarBOT.utils.class_getter import get_user_info, get_fight_room_u


@dp.message_handler(IsPrivate(), text=strings.fight_users_buttons[0])
async def fight_1_vs_1Start(message: types.Message):
    user_info = await get_user_info(message.from_user.id)
    if user_info.city == "coliseum":
        aviable_haracteristics = await user_info.get_aviable_haracteristics()
        # Если локация это не город
        if user_info.current_hp >= aviable_haracteristics[0] / 2:
            wait_check = await check_wait_room(message.from_user.id)
            await DB.delete_add_from_wait_room(message.from_user.id, True)

            if wait_check:
                current_state = dp.current_state(user=message.from_user.id)
                await current_state.set_state(FightStateUser.fight_attack)


            else:
                await FightState.cancel_find.set()
                asyncio.create_task(waiting_room(message.from_user.id))
                await bot.send_message(message.from_user.id, strings.start_find_enemy,
                                       reply_markup=await default.get_fight_res_button(strings.cancel_del))
        else:
            await bot.send_message(message.from_user.id, strings.string_you_not_have_hp)


@dp.message_handler(IsPrivate(), text=[strings.surrender, strings.yes_or_no[0]],
                    state=[FightStateUser.fight_attack, FightStateUser.fight_defence])
async def fight_1_vs_1Surrender(message: types.Message):
    """Сдаться"""
    if message.text == strings.surrender:
        await bot.send_message(message.from_user.id, strings.are_you_sure_surrender,
                               reply_markup=await default.yes_or_no_buttons())
    else:
        fight_room = await get_fight_room_u(message.from_user.id)
        player_2 = await fight_room.get_another_player(message.from_user.id)

        clan_war = await DB.get_clan_war()
        clan_war_active = clan_war[0]

        await DB.delete_fight_room_users(message.from_user.id)

        values = await DB.get_hp(message.from_user.id)
        await DB.set_current_hp(message.from_user.id, values[0], "-")
        # Переносим в другой город
        await DB.set_city(message.from_user.id, "karabah")

        await fight_room.increase_glory_pvp_points(player_2)

        await bot.send_message(message.from_user.id, await strings.gfr("surrender_lose", clan_war_active),
                               reply_markup=await default.get_fight_res_button(strings.take_life))
        await bot.send_message(player_2, await strings.gfr("surrender_win", clan_war_active),
                               reply_markup=await default.get_fight_res_button(strings.take_reward))

        await dp.current_state(user=message.from_user.id, chat=message.from_user.id).finish()
        await dp.current_state(user=player_2, chat=player_2).finish()

        asyncio.create_task(functions.heal_hp(message.from_user.id))
        asyncio.create_task(functions.heal_hp(player_2))


@dp.message_handler(IsPrivate(), state=[FightStateUser.fight_attack, FightStateUser.fight_defence])
async def fight_1_vs_1AttackAndDefence(message: types.Message, state: FSMContext):
    fight_room = await get_fight_room_u(message.from_user.id)
    user_position = await fight_room.get_another_player(message.from_user.id, is_position=True)
    # Если сообщение из доступных
    if message.text in strings.fight_actions_buttons[0:5] or message.text in strings.fight_actions_buttons[5:10]:
        player_do_move = fight_room.user_1_do_move if user_position == 1 else fight_room.user_2_do_move
        # Если пользователь не делал ход
        if not player_do_move:
            action_type = "attack" if message.text in strings.fight_actions_buttons[0:5] else "block"
            # Установим значение какое выбрал игрок
            await DB.set_action_online_fight(message.from_user.id, strings.fight_actions[message.text], action_type,
                                             user_position)
            # Если это атака
            if action_type == "attack":
                user_info = await get_user_info(state.user)
                await bot.send_message(message.from_user.id, strings.what_you_want_to_defaet,
                                       reply_markup=await default.fight_act(False, user_info, is_online=True))
                await state.finish()
                await FightStateUser.fight_defence.set()
            # Если это защита
            else:
                await DB.set_do_move_online(message.from_user.id, 1, user_position)
                another_player_do_move = fight_room.user_1_do_move if user_position == 2 else fight_room.user_2_do_move
                # Если второй игрок сделал ход ранее
                if another_player_do_move:
                    fight_room = await get_fight_room_u(message.from_user.id)
                    res = await fight_room.round_resultat(False, False)

                    another_user_info = await get_user_info(await fight_room.get_another_player(message.from_user.id))
                    user_info = await get_user_info(message.from_user.id)
                    await bot.send_message(message.from_user.id, res,
                                           reply_markup=await default.fight_act(True, user_info, False,
                                                                                is_online=True))
                    await bot.send_message(another_user_info.id, res,
                                           reply_markup=await default.fight_act(True, another_user_info, False,

                                                                                is_online=True))
                    fight_room = await get_fight_room_u(message.from_user.id)

                    if not await round_resultat_end(fight_room):
                        await DB.set_do_move_online(message.from_user.id, 0, user_position)
                        await DB.set_do_move_online(another_user_info.id, 0, 1 if user_position == 2 else 2)

                        await dp.current_state(chat=message.from_user.id, user=message.from_user.id).set_state(
                            FightStateUser.fight_attack)
                        await dp.current_state(chat=another_user_info.id, user=another_user_info.id).set_state(
                            FightStateUser.fight_attack)

                        await move_time(message.from_user.id)

                # Если второй игрок ещё не сделал ход
                else:
                    await bot.send_message(message.from_user.id, strings.wait_res_move,
                                           reply_markup=await default.get_fight_res_button(strings.surrender))

    else:
        # Если сообщение не подходит и оно не доступно как атака или защита
        player_do_move = fight_room.user_1_do_move if user_position == 1 else fight_room.user_2_do_move
        # Если игрок не делал ход
        if not player_do_move:
            user_info = await get_user_info(state.user)
            # Если это атака
            if await state.get_state() == "FightStateUser:fight_attack":
                return await bot.send_message(message.from_user.id, strings.where_you_will_to_hit,
                                              reply_markup=await default.fight_act(True, user_info, True,
                                                                                   is_online=True))
            # Если это защита
            return await bot.send_message(message.from_user.id, strings.what_you_want_to_defaet,
                                          reply_markup=await default.fight_act(False, user_info, is_empty=True,
                                                                               is_online=True))
        # Если пользователь уже сделал ход то пишем что ожидание
        return await bot.send_message(message.from_user.id, strings.wait_res_move,
                                      reply_markup=await default.get_fight_res_button(strings.surrender))


async def move_time(user_id):
    async def send_round_resultat(fr: FightRoomUsers, r):
        user_1_info, user_2_info = await get_user_info(fr.user_id_1), await get_user_info(fr.user_id_2)
        await bot.send_message(user_1_info.id, r,
                               reply_markup=await default.fight_act(True, user_1_info, False, is_online=True))
        await bot.send_message(user_2_info.id, r,
                               reply_markup=await default.fight_act(True, user_2_info, False, is_online=True))

        if not await round_resultat_end(fight_room):
            user_position = await fight_room.get_player_position(user_1_info.id)

            await DB.set_do_move_online(user_1_info.id, 0, user_position)
            await DB.set_do_move_online(user_2_info.id, 0, 1 if user_position == 2 else 2)

            await dp.current_state(chat=user_1_info.id, user=user_1_info.id).set_state(
                FightStateUser.fight_attack)
            await dp.current_state(chat=user_2_info.id, user=user_2_info.id).set_state(
                FightStateUser.fight_attack)

            await move_time(user_1_info.id)

    await asyncio.sleep(config.MOVE_TIME_ONLINE // 2)
    try:
        fight_room = await get_fight_room_u(user_id)
    except TypeError:
        return
    user_1_do_move, user_2_do_move = fight_room.user_1_do_move, fight_room.user_2_do_move

    if not user_1_do_move and await fight_room.check_time(False, fight_room.user_id_1):
        await bot.send_message(fight_room.user_id_1, strings.string_time_sec.format(config.MOVE_TIME_ONLINE // 2))
    if not user_2_do_move and await fight_room.check_time(False, fight_room.user_id_1):
        await bot.send_message(fight_room.user_id_2, strings.string_time_sec.format(config.MOVE_TIME_ONLINE // 2))

    await asyncio.sleep(config.MOVE_TIME_ONLINE // 2)

    try:
        fight_room = await get_fight_room_u(user_id)
    except TypeError:
        return

    user_1_do_move, user_2_do_move = fight_room.user_1_do_move, fight_room.user_2_do_move

    if not user_1_do_move and not user_2_do_move \
            and await fight_room.check_time(True, fight_room.user_id_1) \
            and await fight_room.check_time(True, fight_room.user_id_2):

        await DB.set_random_moves_online(user_id)
        fight_room = await get_fight_room_u(user_id)

        await send_round_resultat(fight_room, await fight_room.round_resultat(text=strings.two_users_skip_move))

    elif not user_1_do_move and await fight_room.check_time(True, fight_room.user_id_1):
        await DB.set_losed_actions(fight_room.user_id_1, await fight_room.get_player_position(fight_room.user_id_1))
        fight_room = await get_fight_room_u(user_id)

        await send_round_resultat(fight_room, await fight_room.round_resultat(user_1_losed=True))

    elif not user_2_do_move and await fight_room.check_time(True, fight_room.user_id_2):
        await DB.set_losed_actions(fight_room.user_id_2, await fight_room.get_player_position(fight_room.user_id_2))
        fight_room = await get_fight_room_u(user_id)

        await send_round_resultat(fight_room, await fight_room.round_resultat(user_2_losed=True))


async def round_resultat_end(fight_room: FightRoomUsers):
    user_info_1 = await get_user_info(fight_room.user_id_1)
    user_info_2 = await get_user_info(fight_room.user_id_2)

    text_1, text_2, reply_markup_1, reply_markup_2 = None, None, None, None

    user_id_1 = user_info_1.id
    user_id_2 = user_info_2.id

    clan_war = await DB.get_clan_war()
    clan_war_active = clan_war[0]

    if user_info_2.current_hp <= 0 and user_info_1.current_hp <= 0:
        await DB.set_city(user_id_1, "karabah")
        await DB.set_city(user_id_2, "karabah")
        text_1, text_2 = await strings.gfr("draw", clan_war_active), await strings.gfr("draw", clan_war_active)
        reply_markup_1, reply_markup_2 = strings.take_life, strings.take_life

    elif user_info_1.current_hp <= 0:
        await fight_room.increase_glory_pvp_points(user_id_2)
        await DB.set_city(user_id_1, "karabah")
        text_1, text_2 = await strings.gfr("default_lose", clan_war_active), await strings.gfr("default_win", clan_war_active)
        reply_markup_1, reply_markup_2 = strings.take_life, strings.take_reward

    elif user_info_2.current_hp <= 0:
        await fight_room.increase_glory_pvp_points(user_id_1)
        await DB.set_city(user_id_2, "karabah")
        text_1, text_2 = await strings.gfr("default_win", clan_war_active), await strings.gfr("default_lose", clan_war_active)
        reply_markup_1, reply_markup_2 = strings.take_reward, strings.take_life

    if text_1 is not None:
        await DB.delete_fight_room_users(user_info_1.id)

        await dp.current_state(chat=user_id_1, user=user_id_1).finish()
        await dp.current_state(chat=user_id_2, user=user_id_2).finish()

        await bot.send_message(user_id_1, text_1, reply_markup=await default.get_fight_res_button(reply_markup_1))
        await bot.send_message(user_id_2, text_2, reply_markup=await default.get_fight_res_button(reply_markup_2))

        asyncio.create_task(functions.heal_hp(user_id_1))
        asyncio.create_task(functions.heal_hp(user_id_2))

    return text_1 is not None


async def waiting_room(user_id):
    user_wait = await DB.check_user_in_wait_room(user_id)
    while user_wait:
        await asyncio.sleep(1)
        user_wait = await DB.check_user_in_wait_room(user_id)
        wait_check = await check_wait_room(user_id)
        if wait_check:
            current_state = dp.current_state(user=user_id)
            await current_state.set_state()

            user_info = await get_user_info(wait_check)
            user_info_cur = await get_user_info(user_id)

            await bot.send_message(user_id, strings.you_finded_opponent.format(await user_info.get_href_userURL()),
                                   reply_markup=await default.fight_act(True, user_info_cur, is_empty=True,
                                                                        is_online=True))
            await bot.send_message(wait_check,
                                   strings.you_finded_opponent.format(await user_info_cur.get_href_userURL()),
                                   reply_markup=await default.fight_act(True, user_info, is_empty=True, is_online=True))

            await current_state.set_state(FightStateUser.fight_attack)

            await DB.delete_add_from_wait_room(user_id, False)
            await DB.delete_add_from_wait_room(wait_check, False)

            await DB.add_fight_room_users(user_id, wait_check)

            await DB.set_last_move_time_online(user_id)
            await move_time(user_id)

            break


async def check_wait_room(user_id):
    """Проверяет, есть ли пользователи в таблице ожиданий которые подходят игроку по уровню"""
    waiting_room_users = await DB.get_wait_room_info()
    user_info = await get_user_info(user_id)
    for user in waiting_room_users:
        if user_info.lvl - 2 <= user[1] <= user_info.lvl + 2 and user[0] != user_id:
            return user[0]

    return False
