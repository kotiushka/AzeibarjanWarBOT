import asyncio
import datetime
import random

from aiogram import types
from aiogram.dispatcher import FSMContext

from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.config import ENEMY_NPC_FIND_TIME
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import default
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src.enemy import Enemy
from AzeibarjanWarBOT.src.trick import Trick
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.state.states import FightState, FightStateUser
from AzeibarjanWarBOT.utils import strings, functions
from AzeibarjanWarBOT.utils.class_getter import get_location, get_user_info, get_enemy_list, get_fight_room, get_resource, get_quest, \
    get_fight_room_u
from AzeibarjanWarBOT.utils.functions import ret_city


@dp.message_handler(IsPrivate(), text=strings.menuMainButtonsList[8])
async def find_fight(message: types.Message, state: FSMContext):
    """⚔ Найти врагов (кнопка)"""
    # Получаем информацию об пользователе и локации
    user_info = await get_user_info(message.from_user.id)
    location = await get_location(user_info.city)
    aviable_haracteristics = await user_info.get_aviable_haracteristics()
    # Если локация это не город
    is_city = not await location.get_is_city if user_info.city == "coliseum" else await location.get_is_city
    if not is_city:
        if user_info.current_hp >= aviable_haracteristics[0] / 2:
            if user_info.healing == 1:
                await DB.set_healing(message.from_user.id, 0)
            if user_info.city != "coliseum":
                # Запускаем поиск
                await FightState.cancel_find.set()
                # Сообщение 🔭 Начался поиск противника, в reply_markup Отменить поиск
                await bot.send_message(message.from_user.id, strings.start_find_enemy,
                                       reply_markup=await default.get_fight_res_button(strings.cancel_del))
                # Запускаем стейт для фильтрации, на промежуток указаный в конфиге
                await fight_state(state, random.randint(ENEMY_NPC_FIND_TIME[0], ENEMY_NPC_FIND_TIME[1]))

        else:
            await bot.send_message(message.from_user.id, strings.string_you_not_have_hp)


async def fight_state(state: FSMContext, sleep_time):
    current_data = datetime.datetime.now().timestamp()
    await state.update_data(timestamp=current_data)
    # Засыпаем
    await asyncio.sleep(sleep_time)

    data = await state.get_data()

    if 'timestamp' in list(data) and data["timestamp"] == current_data:
        if await state.get_state():
            if not await DB.get_fight_room_info(state.user):
                user_info = await get_user_info(state.user)
                enemyes = await get_enemy_list(user_info.city)
                # Рандомно выбираем противника из доступных по уровню и локации
                opponent = random.choice(enemyes)
                # Добавляем в базу сражение
                await DB.add_fight_room(state.user, opponent)
                # Оповещаем об начале сражения
                await bot.send_message(state.user, await strings.you_finded_enemy(opponent),
                                       reply_markup=await default.fight_act(True, user_info, True))
                # Останавливаем прежний стейт и запускаем новый
                await state.finish()
                await FightState.fight_attack.set()
                # Заносим данные в БД
                await DB.set_last_move_npc(state.user)
                # Запуск нашей функции
                asyncio.create_task(time_move(state))

        else:
            await state.finish()


@dp.message_handler(IsPrivate(), text=[strings.take_life, strings.take_reward, strings.to_hunt_loc])
async def fight_last_step(message: types.Message):
    await ret_city(message.from_user.id)


@dp.message_handler(IsPrivate(), state=FightState.cancel_find)
async def cancel_find_fight(message: types.Message, state: FSMContext):
    if message.text == strings.cancel_del:
        asyncio.create_task(functions.heal_hp(message.from_user.id))
        await state.finish()
        await bot.send_message(message.from_user.id, strings.find_fight_canceled)
        await DB.delete_add_from_wait_room(message.from_user.id, False)
        await ret_city(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, strings.you_in_find, reply_markup=await default.get_fight_res_button(
            strings.cancel_del))


@dp.message_handler(IsPrivate(), state=[FightState.fight_attack, FightStateUser.fight_attack],
                    text=strings.tricks_titles)
async def tricks_use(message: types.Message, state: FSMContext):
    """Использование боевых приемов"""
    current_trick = Trick(*await DB.get_trick_with_title(message.text))
    need_round_items = await current_trick.get_need_round_items
    user_info = await get_user_info(message.from_user.id)

    if await DB.check_item_on_inventory(current_trick.id, user_info.nickname):

        is_npc_state = await state.get_state() != "FightStateUser:fight_attack"

        fight_info = await get_fight_room(message.from_user.id) if is_npc_state else await get_fight_room_u(message.from_user.id)

        attack_and_block = await fight_info.attack_and_block(message.from_user.id)
        if need_round_items[0] <= attack_and_block[0] and \
                need_round_items[1] <= attack_and_block[1]:

            await DB.set_last_trick(message.from_user.id, current_trick.id) \
                if is_npc_state else await DB.set_last_trick(
                message.from_user.id,
                current_trick.id,
                await fight_info.get_player_position(message.from_user.id))

            if current_trick.repeat != 0:
                await DB.set_used_tricks(message.from_user.id, current_trick.id) \
                    if is_npc_state else await DB.set_used_tricks(
                    message.from_user.id, current_trick.id, await fight_info.get_player_position(message.from_user.id))

            if need_round_items[0] != 0:
                await DB.update_round_item("attacks", need_round_items[0],
                                           message.from_user.id) if is_npc_state else await DB.update_round_item(
                    "attacks", need_round_items[0], message.from_user.id,
                    await fight_info.get_player_position(message.from_user.id))
            if need_round_items[1] != 0:
                if is_npc_state:
                    await DB.update_round_item("dext", need_round_items[1], message.from_user.id)
                else:
                    await DB.update_round_item("blocks", need_round_items[1], message.from_user.id,
                                               await fight_info.get_player_position(message.from_user.id))

        await bot.send_message(message.from_user.id, strings.where_you_will_to_hit,
                               reply_markup=await default.fight_act(True, user_info, True))


@dp.message_handler(IsPrivate(), state=[FightState.fight_attack, FightState.fight_defence],
                    text=strings.fight_actions_buttons[-1])
async def fight_run(message: types.Message):
    await bot.send_message(message.from_user.id, strings.are_you_sure_run,
                           reply_markup=await default.yes_or_no_buttons())


@dp.message_handler(IsPrivate(), state=[FightState.fight_attack, FightState.fight_defence], text=strings.yes_or_no[0])
async def fight_cancel(message: types.Message, state: FSMContext):
    """Сбежать -> Да"""
    # С шансом 1 из 3 мы можем попробовать сбежать
    if random.randint(1, 3) == 3:
        # Если повезло
        await state.finish()
        # Отправим сообщение что успешно
        await bot.send_message(message.from_user.id, strings.you_successfully_runed,
                               reply_markup=await default.get_fight_res_button(strings.to_hunt_loc))
        # Удалим комнату
        await DB.delete_fight_room(message.from_user.id)
    # Если не повезло
    else:
        # Завершаем стейт
        await state.finish()
        # Отправим сообщение что не успешно
        await bot.send_message(message.from_user.id, strings.you_losed_run,
                               reply_markup=await default.get_fight_res_button(strings.take_life))
        # Сетим хп к нулю
        values = await DB.get_hp(message.from_user.id)
        await DB.set_current_hp(message.from_user.id, values[0], "-")
        # Переносим в другой город
        await DB.set_city(message.from_user.id, "baki")
        # Удалим комнату
        await DB.delete_fight_room(message.from_user.id)
    # Запускаем отхил
    asyncio.create_task(functions.heal_hp(message.from_user.id))


@dp.message_handler(IsPrivate(), state=FightState.fight_attack)
async def fight_attack(message: types.Message, state: FSMContext):
    user_info = await get_user_info(state.user)
    if message.text in strings.fight_actions_buttons[0:5]:
        await DB.set_attack_action(message.from_user.id, strings.fight_actions[message.text], "attack")
        await bot.send_message(message.from_user.id, strings.what_you_want_to_defaet,
                               reply_markup=await default.fight_act(False, user_info))
        await state.finish()
        await FightState.fight_defence.set()
    else:
        await bot.send_message(message.from_user.id, strings.where_you_will_to_hit,
                               reply_markup=await default.fight_act(True, user_info, True))


@dp.message_handler(IsPrivate(), state=FightState.fight_defence)
async def fight_defence(message: types.Message, state: FSMContext):
    user_info = await get_user_info(state.user)
    if message.text in strings.fight_actions_buttons[5:10]:
        fight_room = await get_fight_room(message.from_user.id)
        if not fight_room.can_do_move:
            await DB.set_do_move(message.from_user.id)
            await DB.set_attack_action(message.from_user.id, strings.fight_actions[message.text], "block")
            # заносим в бд что выбрал

            await bot.send_message(message.from_user.id, strings.wait_res_move,
                                   reply_markup=await default.get_fight_res_button(strings.fight_actions_buttons[-1]))
            await asyncio.sleep(random.randint(*config.WAIT_RES_MOVE))
            fight_info = await get_fight_room(state.user)
            # делаем ход
            await bot.send_message(message.from_user.id, await fight_info.get_text_fight(),
                                   reply_markup=await default.fight_act(True, user_info))
            await DB.set_do_move(message.from_user.id)
            await resultat_move(state)

    elif message.text == strings.fight_actions_buttons[10]:
        await DB.set_attack_action(message.from_user.id, strings.fight_actions[message.text], "block")
        await resultat_move(state)

    else:
        # это если сообщение не подходит
        await bot.send_message(message.from_user.id, strings.what_you_want_to_defaet,
                               reply_markup=await default.fight_act(False, user_info))


async def resultat_move(state: FSMContext):
    await state.finish()
    fight_info = await get_fight_room(state.user)
    user_info = await get_user_info(state.user)
    enemy_current_hp = await fight_info.get_enemy_current_hp

    hp = [user_info.current_hp > 0, enemy_current_hp > 0]

    if hp[0] is False or hp[1] is False:
        res = await strings.get_fight_result(hp, await fight_info.get_enemy)

        await DB.delete_fight_room(state.user)
        asyncio.create_task(functions.heal_hp(state.user))

        if res[2]:
            await DB.set_city(state.user, "baki")
            await DB.update_glory(3, '-', user_info.id)
            await bot.send_message(user_info.id, res[0], reply_markup=await default.get_fight_res_button(res[1]))

        else:
            enemy = await fight_info.get_enemy
            resultat = await get_fight_res_loot(user_info, enemy)
            resource = await get_resource(resultat[2])

            bonus_xp_text = f"(+{user_info.bonus_xp}%)" if user_info.bonus_xp != 0 else ""
            bonus_gold_text = f"(+{user_info.bonus_gold}%)" if user_info.bonus_gold != 0 else ""

            # Получим окончательный текст про бой и отправим, что пользователь побелил
            text = res[0] + "\n" + strings.get_received_reward.format(resultat[0], bonus_xp_text, resultat[1], bonus_gold_text, resource.title)
            await bot.send_message(user_info.id, text, reply_markup=await default.get_fight_res_button(res[1]))
            await DB.add_item_to_inventory(user_info.nickname, resource.type, resource.item_id)

            # Задействуем изменение уровня и золота после отправки сообщения
            await add_enemy_quest(user_info.id, enemy.id)
            await DB.update_glory(3, '+', user_info.id)
            await functions.increase_player_level(user_info, resultat[0])
            await DB.update_balance(resultat[1], "+", user_info.id)

    else:
        await FightState.fight_attack.set()
        await DB.set_last_move_npc(state.user)


async def add_enemy_quest(user_id, enemy_name):
    for quest_id in await DB.get_quest_user(user_id):
        current_quest = await get_quest(quest_id[0])
        enemy_type = current_quest.quest_type_req.split("_")[1]
        if enemy_name == enemy_type or enemy_type == "all":
            await DB.add_received_quest(user_id, current_quest.id)





async def get_fight_res_loot(user_info: User, enemy: Enemy):
    lvl_boost = enemy.get_xp
    gold_add = enemy.get_gold

    lvl_boost = lvl_boost + lvl_boost / 100 * user_info.bonus_xp if user_info.bonus_xp != 0 else lvl_boost
    gold_add = gold_add + gold_add / 100 * user_info.bonus_gold if user_info.bonus_gold != 0 else gold_add

    return [round(lvl_boost), round(gold_add), random.choice(enemy.get_loot)]


async def time_move(state: FSMContext):
    await_time = config.WAIT_MOVE_TIME // 2

    # Цикл пока рума существует
    while await DB.get_bool_npcRoom(state.user):
        notify = False
        while True:
            # Засыпаем на половину времени
            await asyncio.sleep(await_time)
            try:
                # Если текущее время - время последнего хода >= половины времени ожидания
                npc_last_move = await DB.get_last_move_time_npc(state.user)
                if notify is False and datetime.datetime.now().timestamp() - npc_last_move >= await_time:
                    # Пишем что прошла половина времени
                    await bot.send_message(state.user, strings.string_time_sec.format(config.WAIT_MOVE_TIME // 2))
                    notify = True

                elif datetime.datetime.now().timestamp() - npc_last_move >= await_time * 2:
                    _state = await state.get_state()

                    fight_info = await get_fight_room(state.user)

                    # Пишем челу что он пропустил ход, выводим инфу о раунде
                    user_info = await get_user_info(state.user)
                    await bot.send_message(state.user, await fight_info.get_text_fight(True),
                                           reply_markup=await default.fight_act(True, user_info))

                    # Это надо для проверки и запуска нового стейта
                    await resultat_move(state)
                    break
            except TypeError:
                return





