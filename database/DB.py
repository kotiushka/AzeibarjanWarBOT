import random
from datetime import datetime, timedelta
from random import randint

import aiosqlite

from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.src.enemy import Enemy
from AzeibarjanWarBOT.src.potion import Potion
from AzeibarjanWarBOT.src.user import User

PATH_TO_DB = 'database/azerbaijan_bot.db'


# Проверка пользователя в базе данных
async def user_check(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        return bool(await cursor.fetchone())


# Добавление юзера в бд бота
async def user_add(user_id, username):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username,))
        return await connection.commit()


# Сетим рассу
async def set_course(course, user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET course=? WHERE id=?", (course, user_id,))
        return await connection.commit()


# Сетим никнейм
async def set_nickname(nickname, user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET nickname=? WHERE id=?", (nickname, user_id,))
        return await connection.commit()


async def get_busy_name(nickname):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT nickname FROM users WHERE nickname=?", (nickname,))
        return bool(await cursor.fetchone())


async def update_balance(num, operand, user_id, is_coupon=False):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        currency = "gold" if not is_coupon else "coupon"
        await connection.execute(f"UPDATE users SET {currency}={currency}{operand}{num} WHERE id=?", (user_id,))
        return await connection.commit()


async def add_item_to_inventory(nickname, item_type, item, up_lvl=0):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("INSERT INTO inventory (nickname, item_type, item_name, up_lvl) VALUES (?, ?, ?, ?)",
                                 (nickname, item_type, item, up_lvl,))

        return await connection.commit()


async def get_use_items_from_inventory(nickname):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT weapon, helmet, armor, gloves, boots, shield, ring, necklace, accessory FROM "
                             "users WHERE nickname = ?", (nickname,))
        return await cursor.fetchone()


async def get_all_items_from_inventory(nickname):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT item_type, item_name FROM inventory WHERE nickname = ?",
                             (nickname,))
        return await cursor.fetchall()


async def get_item_count(nickname, item):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT COUNT(item_type) FROM inventory WHERE item_type = ? AND nickname = ?",
                             (item, nickname,))
        res = await cursor.fetchone()
        return res[0]


async def get_current_items(nickname, item_type, is_res=True):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        if is_res:
            await cursor.execute(
                "SELECT item_name, item_id FROM inventory WHERE item_type = ? AND nickname = ? ORDER BY use DESC",
                (item_type, nickname,))
            return await cursor.fetchall()
        result = []
        for equip in dicts.equip_types:
            await cursor.execute("SELECT item_name, item_id FROM inventory WHERE item_type=? AND nickname=?",
                                 (equip, nickname,))
            eq = await cursor.fetchall()
            if eq:
                for item in eq:
                    result.append(item)
        return result


async def get_item(id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM items WHERE id=?", (id,))
        return await cursor.fetchone()


async def get_user_info(id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM users WHERE id=?", (id,))
        return await cursor.fetchone()


async def get_item_use(item_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT use, up_lvl FROM inventory WHERE item_id=?",
                             (item_id,))
        return await cursor.fetchone()


async def set_item_use(item_id, value):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE inventory SET use=?  WHERE item_id=?", (value, item_id,))
        return await connection.commit()


async def get_use_item_bool(user_id, item_type):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        if item_type in ["sword", "axe", "dagger"]:
            await cursor.execute(f"SELECT weapon FROM users WHERE id=?", (user_id,))
            res = await cursor.fetchone()
            return [bool(res[0]), res[0]]
        await cursor.execute(f"SELECT {item_type} FROM users WHERE id=?", (user_id,))
        res = await cursor.fetchone()
        result = (res[0])
        return [bool(result), result]


async def get_current_item_from_inventory(nickname, item_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM inventory WHERE nickname = ? AND item_id = ?",
                             (nickname, item_id,))
        return await cursor.fetchone()


async def use_item_upper(user_id, bonus, value, operation="+"):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute(f"SELECT {bonus} FROM users WHERE id=?", (user_id,))
        res = await cursor.fetchone()
        current_bonus = res[0]
        if operation == "+":
            await connection.execute(f"UPDATE users SET {bonus}=? WHERE id=?", (current_bonus + value, user_id,))
            return await connection.commit()
        if bonus == "max_hp":
            hp = await get_hp(user_id)
            current_hp = hp[0]
            max_hp = hp[1]

            if current_hp > max_hp - value:
                await connection.execute(f"UPDATE users SET current_hp=? WHERE id=?", (current_bonus - value, user_id,))

        await connection.execute(f"UPDATE users SET {bonus}=? WHERE id=?", (current_bonus - value, user_id,))
        return await connection.commit()


async def set_item_use_users(item_name, item_type, user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if item_type in ["sword", "axe", "dagger"]:
            item_type = "weapon"
        await connection.execute(f"UPDATE users SET {item_type}=? WHERE id=?", (item_name, user_id,))
        return await connection.commit()


async def up_item_lvl(item_id, lvl):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE inventory set up_lvl=? WHERE item_id=?", (lvl, item_id,))
        return await connection.commit()


async def select_resource(resource_name, nickname):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute(f"SELECT item_id FROM inventory WHERE nickname=? AND item_name=?",
                             (nickname, resource_name,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        return None


async def delete_from_inventory(item_id, nickname):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("DELETE FROM inventory WHERE item_id=? AND nickname=?", (item_id, nickname,))
        return await connection.commit()


async def get_hp(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT current_hp, max_hp, lvl, healing FROM users WHERE id=?",
                             (user_id,))
        return await cursor.fetchone()


async def set_current_hp(user_id, value=1, operand="+", max_hp=None):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if operand == "+":
            if max_hp:
                await connection.execute(
                    "UPDATE users SET current_hp = CASE WHEN current_hp + ? > max_hp THEN max_hp ELSE current_hp + ? END WHERE id = ?",
                    (value, value, user_id))

            else:
                await connection.execute(f"UPDATE users SET current_hp=current_hp+{value} WHERE id=?", (user_id,))

            return await connection.commit()
        await connection.execute("UPDATE users SET current_hp = MAX(current_hp - ?, 0) WHERE id = ?", (value, user_id,))
        return await connection.commit()


async def set_healing(user_id, num):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET healing=? WHERE id=?", (num, user_id,))
        return await connection.commit()


async def get_trick(id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM tricks WHERE id=?", (id,))
        return await cursor.fetchone()


async def check_item_on_inventory(item_name, nickname):
    """Проверка, есть ли предмет в инвентаре"""
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM inventory WHERE item_name=? AND nickname=?",
                             (item_name, nickname,))
        return bool(await cursor.fetchone())


async def get_item_inventory_name(nickname, item_name):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM inventory WHERE nickname = ? AND item_name=?",
                             (nickname, item_name,))
        res = await cursor.fetchone()
        return res[0]


async def update_trick(id, trick_slot, value=False):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if value is False:
            value = None
        await connection.execute(f"UPDATE users SET trick_{trick_slot}=? WHERE id=?", (value, id,))
        return await connection.commit()


async def get_location(id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM locations WHERE id=?", (id,))
        return await cursor.fetchone()


async def get_location_id(name):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT id FROM locations WHERE name=?", (name,))
        res = await cursor.fetchone()
        return res[0]


async def set_city(user_id, city):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET city=? WHERE id=?", (city, user_id,))
        return await connection.commit()


async def get_enemy_list(current_location):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM opponents WHERE location=?",
                             (current_location,))
        return await cursor.fetchall()


async def get_enemy(enemy_id) -> Enemy:
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM opponents WHERE id = ?", (enemy_id,))
        return Enemy(*await cursor.fetchone())


async def add_fight_room(user_id, enemy):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute(
            "INSERT INTO fight_room_npc (user_id, enemy_id, enemy_current_hp) VALUES (?, ?, ?)",
            (user_id, enemy.id, enemy.max_hp,))
        return await connection.commit()


async def set_attack_action(user_id: int, value: int, type: str, type_person="user"):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(f"UPDATE fight_room_npc SET {type_person}_{type}=? WHERE user_id=?",
                                 (value, user_id))
        return await connection.commit()


async def get_fight_room_info(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM fight_room_npc WHERE user_id = ?",
                             (user_id,))
        return await cursor.fetchone()


async def update_move(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(f"UPDATE fight_room_npc SET move = move + 1 WHERE user_id = ?", (user_id,))
        return await connection.commit()


async def get_move(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute(f"SELECT move FROM fight_room_npc WHERE user_id = ?",
                             (user_id,))
        res = await cursor.fetchone()
        return res[0]


async def set_enemy_current_hp(user_id, value):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            f"UPDATE fight_room_npc SET enemy_current_hp = enemy_current_hp - {value} WHERE user_id = ?", (user_id,))
        return await connection.commit()


async def get_enemy_current_hp(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT enemy_current_hp FROM fight_room_npc WHERE user_id = ?", (user_id,))
        res = await cursor.fetchone()
        return res[0]


async def delete_fight_room(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("DELETE FROM fight_room_npc WHERE user_id = ?", (user_id,))
        return await connection.commit()


async def up_skill(user_id, skill_type):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(f"UPDATE fight_room_npc SET {skill_type} = {skill_type}+1 WHERE user_id=?",
                                 (user_id,))
        return await connection.commit()


async def get_skill(user_id, skill_type):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute(f"SELECT {skill_type} FROM fight_room_npc WHERE user_id = ?", (user_id,))
        res = await cursor.fetchone()
        return res[0]


async def get_bool_npcRoom(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM fight_room_npc WHERE user_id = ?", (user_id,))
        return bool(await cursor.fetchone())


async def get_last_move_time_npc(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT last_move_time FROM fight_room_npc WHERE user_id = ?", (user_id,))
        res = await cursor.fetchone()
        return res[0]


async def set_last_move_npc(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            f"UPDATE fight_room_npc SET last_move_time = {int(datetime.now().timestamp())} WHERE user_id=?",
            (user_id,))
        return await connection.commit()


async def get_trick_with_title(trick_title):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM tricks WHERE title=?", (trick_title,))
        return await cursor.fetchone()


async def set_last_trick(user_id, trick_id, user_position=None):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if not user_position:
            await connection.execute("UPDATE fight_room_npc SET user_last_trick=? WHERE user_id=?",
                                     (trick_id, user_id,))
        else:
            await connection.execute(
                f"UPDATE fight_room_users SET user_{user_position}_last_trick=? WHERE user_id_1 = ? OR user_id_2 = ?",
                (trick_id, user_id, user_id,))

        return await connection.commit()



async def set_used_tricks(user_id, trick_id, user_position=None):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()

        if user_position:
            query = f"UPDATE fight_room_users SET user_{user_position}_tricks = CASE WHEN user_{user_position}_tricks IS NULL THEN ? ELSE user_{user_position}_tricks || ? END WHERE user_id_1 = ? OR user_id_2 = ?"
            await cursor.execute(query, (trick_id + " ", trick_id + " ", user_id, user_id))

        else:
            query = "UPDATE fight_room_npc SET used_tricks = CASE WHEN used_tricks IS NULL THEN ? ELSE used_tricks || ? END WHERE user_id = ?"
            await cursor.execute(query, (trick_id + " ", trick_id + " ", user_id))

        return await connection.commit()


async def update_round_item(item, value, user_id, user_position=None):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if item in ["dext", "attacks", "blocks"]:
            if not user_position:
                await connection.execute(f"UPDATE fight_room_npc SET {item}={item}-{value} WHERE user_id=?", (user_id,))
            else:
                await connection.execute(f"UPDATE fight_room_users SET user_{user_position}_{item}=user_{user_position}_{item}-{value} WHERE user_id_1 = ? OR user_id_2 = ?", (user_id, user_id,))

            return await connection.commit()

        else:
            raise TypeError

async def get_npc_actions_fight_room(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT npc_attack, npc_block FROM fight_room_npc WHERE user_id=?",
                             (user_id,))
        return await cursor.fetchone()


async def clear_last_trick(user_id, user_position=None):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if not user_position:
            await connection.execute("UPDATE fight_room_npc SET user_last_trick=? WHERE user_id=?", (None, user_id))
        else:
            await connection.execute(f"UPDATE fight_room_users SET user_{user_position}_last_trick=? WHERE user_id_1 = ? OR user_id_2 = ?", (None, user_id, user_id,))

        return await connection.commit()


async def select_top_info(value):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        if value != "clan_top":
            await cursor.execute(
                f"SELECT id, nickname, course, lvl, glory, pvp_points, gold FROM users ORDER BY {value} DESC")
            return await cursor.fetchall()

        else:
            clans = await select_all_clans("")
            resultat = []
            for res in clans:
                await cursor.execute("SELECT SUM(pvp_points) FROM users WHERE clan=? ORDER BY pvp_points DESC", (res[0],))
                clan_sum = await cursor.fetchone()
                resultat.append([res[0], clan_sum[0]])

            resultat.sort(key=lambda x: x[1], reverse=True)
            return resultat


async def up_point_skill(user_id, value):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(f"UPDATE users SET {value}={value}+1 WHERE id={user_id}")
        return await connection.commit()


async def change_stat_point(user_id, value, operand):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(f"UPDATE users SET stat_point=stat_point{operand}{value} WHERE id={user_id}")
        return await connection.commit()


async def get_resource(item_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM resources WHERE item_id=?", (item_id,))
        return await cursor.fetchone()


async def get_resources_list():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT item_id, title FROM resources")
        return await cursor.fetchall()


async def reset_params(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        values = ["force", "power", "dexterity", "intuition"]
        points = 0
        for i in values:
            await cursor.execute(f"SELECT {i} FROM users WHERE id=?", (user_id,))
            count_points = await cursor.fetchone()
            points += count_points[0]
            await connection.execute(f"UPDATE users SET {i}=0 WHERE id=?", (user_id,))
        await connection.execute("UPDATE users SET current_hp=max_hp, stat_point= stat_point + ? WHERE id=?",
                                 (points, user_id,))
        return await connection.commit()


async def get_resources(nickname: str, item_type: str) -> list[list]:
    """Извлекаем из инвентаря название предмета с определенным типом"""
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        res = []
        await cursor.execute("SELECT item_type, item_name FROM inventory WHERE nickname=? and item_type=?",
                             (nickname, item_type,))
        item_info = set(await cursor.fetchall())
        for i in item_info:
            if i is not None:
                await cursor.execute("SELECT COUNT(*) FROM inventory WHERE nickname=? AND item_name=?",
                                     (nickname, i[1],))
                item_count = await cursor.fetchone()
                res.append([*i, item_count[0]])

        return res


async def delete_all_info_about_person(user_id, nickname):
    """
    Удаляет ВСЮ информацию об игроке
    :param user_id: айди пользователя
    :param nickname: ник пользователя
    """
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("DELETE FROM users WHERE id=?", (user_id,))
        await connection.execute("DELETE FROM inventory WHERE nickname=?", (nickname,))
        await connection.execute("DELETE FROM clan_users WHERE user_id=?", (user_id,))
        return await connection.commit()


async def change_nickname_person(user_id, old_nickname, new_nickname):
    """Изменяет ник игрока"""
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET nickname=? WHERE id=?", (new_nickname, user_id,))
        await connection.execute("UPDATE inventory SET nickname=? WHERE nickname=?", (new_nickname, old_nickname,))
        return await connection.commit()


async def change_user_lvl(user_id, new_lvl: int, new_count_exp: int):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET current_xp=?, lvl=? WHERE id=?", (new_count_exp, new_lvl, user_id,))
        return await connection.commit()


async def update_glory(num, operand, user_id, column_type="glory"):
    async with aiosqlite.connect(PATH_TO_DB) as connection:

        if operand == "-":
            cursor = await connection.cursor()
            await cursor.execute(f"SELECT {column_type} FROM users WHERE id=?", (user_id,))
            current_glory = await cursor.fetchone()
            if (current_glory[0] - num) < 0:
                await connection.execute(f"UPDATE users SET {column_type}=0 WHERE id=?", (user_id,))
            else:
                await connection.execute(f"UPDATE users SET {column_type}={column_type}-{num} WHERE id=?", (user_id,))
        else:
            await connection.execute(f"UPDATE users SET {column_type}={column_type}+{num} WHERE id=?", (user_id,))

        return await connection.commit()


async def set_full_hp(max_hp, user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET current_hp=? WHERE id=?", (max_hp, user_id,))
        return await connection.commit()


async def get_count_items_from_inventory(item_id, nickname, with_item_name=False):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute(f"SELECT COUNT(*) FROM inventory WHERE {'item_id' if not with_item_name else 'item_name'}=? AND nickname=?", (item_id, nickname,))
        res = await cursor.fetchone()
        return res[0]


async def select_all_items(table, querry_params, search_space):
    aviable_tables = ["opponents", "resources", "tricks", "items", "users"]
    if table in aviable_tables:
        async with aiosqlite.connect(PATH_TO_DB) as connection:
            cursor = await connection.cursor()
            if querry_params != "":
                await cursor.execute(f"SELECT * FROM {table} WHERE LOWER({search_space}) LIKE '%{querry_params}%'")
            else:
                await cursor.execute(f"SELECT * FROM {table}")

            return await cursor.fetchall()
    raise TypeError


async def select_clan_users(querry_params):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM clan_users WHERE id=?", (int(querry_params),))
        return await cursor.fetchall()


async def select_all_clans(querry_params):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute(
            f"SELECT clans.id, clans.name, count(*) as clan_users_count FROM clan_users JOIN clans ON clans.id = clan_users.id WHERE LOWER(clans.name) LIKE '%{querry_params}%' GROUP by clans.name")
        return await cursor.fetchall()


async def get_recourse_res(item_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute(
            "SELECT resources.title FROM crafters INNER JOIN resources ON crafters.result = resources.id WHERE crafters.id = ?",
            (item_id,))
        result = await cursor.fetchone()
        return result[0]


async def delete_from_inventory_with_item_name(item_name, nickname, limit=1):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(f"DELETE FROM inventory WHERE item_name=? AND nickname=? LIMIT {limit}",
                                 (item_name, nickname,))
        return await connection.commit()


async def get_potion(potion_name: str) -> Potion:
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM potions WHERE id = (SELECT id FROM resources WHERE item_id = ?)",
                             (potion_name,))
        return Potion(*await cursor.fetchone())


async def use_potion(user_info: User, bonus: list, operand: str):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        bonus_value = bonus[1]
        bonus = bonus[0]

        if bonus == "current_hp":
            if operand == "+":
                haracteristics = await user_info.get_aviable_haracteristics()
                with_bonus = user_info.current_hp + bonus_value
                max_hp = haracteristics[0]

                if with_bonus > max_hp:
                    await connection.execute("UPDATE users SET current_hp=? WHERE id=?", (max_hp, user_info.id))
                else:
                    await connection.execute("UPDATE users SET current_hp=? WHERE id=?", (with_bonus, user_info.id))

        else:
            if operand == "+":
                await connection.execute(f"UPDATE users SET {bonus}={bonus_value} WHERE id=?",
                                         (user_info.id,))
            elif operand == "-":
                await remove_current_potion(user_info.id, bonus)
                await connection.execute(f"UPDATE users SET {bonus}=0 WHERE id=?",
                                         (user_info.id,))

        return await connection.commit()


async def remove_current_potion(user_id, bonus):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        user_info = User(*await get_user_info(user_id))
        potions = user_info.current_potions
        if bonus in potions:
            potions = potions.remove(bonus)
            resultat = [f"{eff} " for eff in potions] if potions else []

            await connection.execute("UPDATE users SET current_potions=? WHERE id=?",
                                     ("".join(resultat), user_info.id,))
        return await connection.commit()


async def set_do_move(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            "UPDATE fight_room_npc SET can_do_move = CASE WHEN can_do_move = 0 THEN 1 WHEN can_do_move = 1 THEN 0 END WHERE user_id=?",
            (user_id,))
        return await connection.commit()


async def get_trade_room(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM trade_room WHERE user_1 =? OR user_2 = ?", (user_id, user_id,))
        return await cursor.fetchone()


async def create_trade_room(user_id_1, user_id_2):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("INSERT INTO trade_room (id, user_1, user_2) VALUES (?, ?, ?)",
                                 (randint(10000, 99999), user_id_1, user_id_2,))
        return await connection.commit()


async def delete_trade_room(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("DELETE FROM trade_room WHERE user_1 = ? OR user_2 = ?", (user_id, user_id,))
        return await connection.commit()


async def update_coupon_gold(user_id, user_position, currency_type, value):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            f"UPDATE trade_room SET {currency_type}_{user_position} = {currency_type}_{user_position} + ? WHERE user_{user_position}=?",
            (value, user_id,))
        return await connection.commit()


async def add_equip_res(user_id, user_position, item_type, item):
    if item_type in ["equip", "resources"]:
        async with aiosqlite.connect(PATH_TO_DB) as connection:
            async with connection.execute("BEGIN"):
                sql = f"UPDATE trade_room SET {item_type}_{user_position} = (SELECT {item_type}_{user_position} || ' ' || ? FROM trade_room WHERE user_{user_position} = ?) WHERE user_{user_position} = ?"
                params = (item, user_id, user_id)
                await connection.execute(sql, params)
            return await connection.commit()
    raise TypeError


async def set_ready_offer(user_id, position, value: int):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            f"UPDATE trade_room SET ready_{position} = ? WHERE user_1=? OR user_2=?", (value, user_id, user_id,))

        return await connection.commit()


async def get_bool_tradeRoom(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM trade_room WHERE user_1=? OR user_2=?", (user_id, user_id,))
        return await cursor.fetchone() is not None


async def get_clan_busy_name(clan_name):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM clans WHERE name = ?", (clan_name,))
        return await cursor.fetchone() is not None


async def create_clan(clan_name):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("INSERT INTO clans (name) VALUES (?)", (clan_name,))
        return await connection.commit()


async def add_user_to_clan(clan_name, user_id, is_admin=False):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            "INSERT INTO clan_users (id, user_id, is_admin) VALUES ((SELECT id FROM clans WHERE name=?), ?, ?)",
            (clan_name, user_id, 2 if is_admin else 0,))
        await connection.execute("UPDATE users SET clan=(SELECT id FROM clans WHERE name=?) WHERE id=?",
                                 (clan_name, user_id,))
        return await connection.commit()


async def get_user_clan(user_id: int):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM clans WHERE id=(SELECT id FROM clan_users WHERE user_id = ?)", (user_id,))
        return await cursor.fetchone()


async def get_user_clan_id(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT id FROM clan_users WHERE user_id = ?", (user_id,))
        res = await cursor.fetchone()
        return res[0]


async def cancel_clan_creating(user_id):
    try:
        clan = await get_user_clan_id(user_id)
    except TypeError:
        return
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("DELETE FROM clan_users WHERE id=?", (clan,))
        await connection.execute("DELETE FROM clans WHERE id=?", (clan,))
        await connection.execute("UPDATE users SET clan=? WHERE id=?", (None, user_id,))
        return await connection.commit()


async def select_clan_emojies():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM clan_emojies")
        return await cursor.fetchall()


async def add_aviable_emojies(clan_id, emoji_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE clans SET aviable_emojies = aviable_emojies || ' ' || ? WHERE id=?",
                                 (emoji_id, clan_id,))
        return await connection.commit()


async def set_clan_emoji(clan_id, emoji_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE clans SET current_emoji=? WHERE id=?", (emoji_id, clan_id,))
        return await connection.commit()


async def get_clan_emoji(emoji_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT char from clan_emojies WHERE id=?", (emoji_id,))
        result = await cursor.fetchone()
        return "" if result is None else result[0]


async def get_clan_users_count(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        user_clan = await get_user_clan(user_id)
        await cursor.execute("SELECT COUNT(*) FROM clan_users WHERE id=?", (user_clan[0],))
        res = await cursor.fetchone()
        return res[0]


async def get_clan_users_count_with_clan_id(clan_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT COUNT(*) FROM clan_users WHERE id=?", (clan_id,))
        res = await cursor.fetchone()
        return res[0]


async def get_clan_user(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM clan_users WHERE user_id=?", (user_id,))
        res = await cursor.fetchone()
        return res


async def cick_user(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("DELETE FROM clan_users WHERE user_id=?", (user_id,))
        await connection.execute("UPDATE users SET clan=? WHERE id=?", (None, user_id,))
        return await connection.commit()


async def set_unset_clan_pre_head(user_id, value):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE clan_users SET is_admin=? WHERE user_id=?", (value, user_id,))
        return await connection.commit()


async def get_clan_leader(clan_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT user_id FROM clan_users WHERE id=? AND is_admin=2", (clan_id,))
        res = await cursor.fetchone()
        return res[0]


async def get_clans():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM clans LIMIT 10")
        return await cursor.fetchall()


async def get_clan_info_with_clan_id(clan_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM clans WHERE id=?", (clan_id,))
        return await cursor.fetchone()


async def get_pvp_points_clan(clan_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT SUM(pvp_points) FROM users WHERE clan=?", (clan_id,))
        res = await cursor.fetchone()
        return res[0]


async def set_invites_join(user_id, value):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET clan_invite_join=? WHERE id=?", (value, user_id,))
        return await connection.commit()


async def get_pre_heads(clan_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT user_id FROM clan_users WHERE id=? AND is_admin=1", (clan_id,))
        return await cursor.fetchall()


async def add_clan_invites(clan_id, user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET clan_invites=clan_invites || ' ' || ? WHERE id=?",
                                 (clan_id, user_id,))
        return await connection.commit()


async def add_current_potion(potion_id, user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET current_potions=current_potions || ' ' || ? WHERE id=?",
                                 (potion_id, user_id,))
        return await connection.commit()


async def delete_clan_invite(user_id, clans: list[int], clan_id_to_delete: int, all_invites: bool):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if not all_invites:
            clans.remove(clan_id_to_delete)
            resultat = []
            for clan_invite in clans:
                resultat.append(f"{clan_invite} ")
            await connection.execute("UPDATE users SET clan_invites=? WHERE id=?", ("".join(resultat), user_id,))

        else:
            await connection.execute("UPDATE users SET clan_invites='' WHERE id=?", (user_id,))
        return await connection.commit()


async def delete_clan_invite_join(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET clan_invite_join=? WHERE id=?", (None, user_id,))
        return await connection.commit()


async def get_want_to_join_users(clan_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT id FROM users WHERE clan_invite_join=?", (clan_id,))
        return await cursor.fetchall()


async def update_clan_title(clan_id, clan_name):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE clans SET name=? WHERE id=?", (clan_name, clan_id,))
        return await connection.commit()


async def delete_clan(clan_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET clan=? WHERE clan=?", (None, clan_id,))
        await connection.execute("DELETE FROM clans WHERE id=?", (clan_id,))
        await connection.execute("DELETE FROM clan_users WHERE id=?", (clan_id,))
        return await connection.commit()


async def update_last_action(time: int, user_id: int):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET last_action=? WHERE id=?", (time, user_id,))
        return await connection.commit()


async def get_last_action_in_city(location):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT COUNT(*) FROM users WHERE ?-last_action < 60 AND city=?",
                             (datetime.now().timestamp(), location,))
        res = await cursor.fetchone()
        return res[0]


async def get_quest(quest_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM quests WHERE id=?", (quest_id,))
        return await cursor.fetchone()


async def select_today_quests(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM today_quests WHERE user_id =?", (user_id,))
        return await cursor.fetchall()


async def get_quest_user_received(user_id, quest_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT received FROM quests_users WHERE id=? AND user_id=?", (quest_id, user_id,))
        resultat = await cursor.fetchone()
        return None if resultat is None else resultat[0]


async def check_quest_user(user_id, quest_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM quests_users WHERE id=? AND user_id=?", (quest_id, user_id,))
        return bool(await cursor.fetchone())


async def add_quest_users(user_id, quest_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("INSERT INTO quests_users (id, user_id) VALUES (?,?)", (quest_id, user_id,))
        return await connection.commit()


async def delete_quest_users(user_id, quest_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("DELETE FROM quests_users WHERE id=? AND user_id=?", (quest_id, user_id,))
        return await connection.commit()


async def get_quest_user(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT id FROM quests_users WHERE user_id=?", (user_id,))
        resultat = await cursor.fetchall()
        return None if resultat is None else resultat


async def change_succes_quest(user_id, quest_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            "UPDATE quests_users SET succes = CASE WHEN succes=0 THEN 1 WHEN succes=1 THEN 0 END WHERE user_id=? AND id=?",
            (user_id, quest_id,))
        return await connection.commit()


async def get_succes_quest(user_id, quest_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        cursor = await connection.cursor()
        await cursor.execute("SELECT succes FROM quests_users WHERE user_id=? and id=?", (user_id, quest_id,))
        res = await cursor.fetchone()
        return res[0]


async def add_received_quest(user_id, quest_id, value=None):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if value is None:
            await connection.execute("UPDATE quests_users SET received = received + 1 WHERE user_id=? AND id=?",
                                     (user_id, quest_id,))
        else:
            await connection.execute(
                f"UPDATE quests_users SET received = CASE WHEN {value}+received > (SELECT required FROM quests WHERE id={quest_id}) THEN (SELECT required FROM quests WHERE id={quest_id}) ELSE {value}+received END WHERE user_id={user_id} AND id={quest_id}")

        return await connection.commit()


async def add_today_quests(user_id, lvl):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT id FROM quests WHERE lvl <= ?", (lvl,))
            resultat = {quest_id[0] for quest_id in await cursor.fetchall()}

            selected = set()
            while len(selected) < 5 and resultat:
                quest_id = random.choice(list(resultat))
                selected.add(quest_id)
                resultat.discard(quest_id)

            await cursor.execute("SELECT id FROM today_quests WHERE user_id = ?", (user_id,))
            existing_quests = {quest_id[0] for quest_id in await cursor.fetchall()}

            for quest in selected:
                if quest not in existing_quests:
                    current_quest = await get_quest(quest)
                    await cursor.execute("INSERT INTO today_quests (id, user_id) VALUES (?,?)", (current_quest[0], user_id,))

            await connection.commit()


async def clear_quests():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("DELETE FROM today_quests")
        await connection.execute("DELETE FROM quests_users")
        return await connection.commit()


# async def add_quests():
#     async with aiosqlite.connect(path_to_db) as connection:
#         cursor = await connection.cursor()
#         enemy_info = await cursor.execute("SELECT * FROM opponents")
#         enemy_info = await enemy_info.fetchall()
#         enemy_list = [Enemy(*res) for res in enemy_info]
#         for _ in range(0, 6):
#             for enemy in enemy_list:
#                 count_enemyes_req = randint(1, 10)
#
#                 count_xp_reward = count_enemyes_req * randint(enemy_rewards[enemy.location][0], enemy_rewards[enemy.location][1])
#                 count_gold_reward = random.randint(5, 15)
#
#                 cur_location = await get_location(enemy.location)
#                 await connection.execute("INSERT INTO quests (quest_type_req, title, description, required, reward_xp, reward_gold, lvl) VALUES(?,?,?,?,?,?,?)", (
#                     f"enemy_{enemy.id}",
#                     f"Убить {count_enemyes_req} {enemy.name}",
#                     f"Тебе нужно убить {count_enemyes_req} врагов {enemy.name}.\n\n<i>Этого врага можно встретить в локации {dicts.transitions_v2[enemy.location]}.</i>",
#                     count_enemyes_req,
#                     count_xp_reward,
#                     count_gold_reward // 1.5,
#                     cur_location[4],
#                 ))
#
#         return await connection.commit()
#
#
# enemy_rewards = {
#     "river": [60, 85],
#     "house_in_the_forest": [90, 110],
#     "wasteland": [140, 170],
#     "hotbed_of_resistance": [224, 250],
#     "cursed_lands": [280, 320],
#     "zealot_camp": [400, 450],
# }


async def check_referal(referal_id, main_user):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT referals FROM users WHERE id=?", (main_user,))
            resultat = await cursor.fetchone()
            if resultat is not None:
                resultat = resultat[0]
                referal_id = str(referal_id)
                for referal in resultat.split():
                    if referal == referal_id:
                        return False
                return True
            return False


async def add_refelal(user_id, referal_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET referals=referals || ' ' || ? WHERE id=?",
                                 (referal_id, user_id,))
        return await connection.commit()


async def create_event(data: dict):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("DELETE FROM event")
        await connection.execute(
            "INSERT INTO event (name, description, resources, gold, coupons) VALUES (?, ?, ?, ?, ?)",
            (data["name"], data["desc"], data["resources"], data["gold"], data["coupons"],))
        return await connection.commit()


async def get_event():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM event")
            return await cursor.fetchone()


async def set_event_reward(user_id, value, all_users=False):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if not all_users:
            await connection.execute(
                "UPDATE users SET event_reward = ? WHERE id=?",
                (value, user_id,))
        else:
            await connection.execute(
                "UPDATE users SET event_reward = ?",
                (value,))
        return await connection.commit()


# ---
async def get_wait_room_info():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT users.id, users.lvl FROM waiting_room JOIN users ON waiting_room.user_id = users.id")
            return await cursor.fetchall()


async def delete_add_from_wait_room(user_id: int, add: bool):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        if add:
            await connection.execute("INSERT INTO waiting_room (user_id) VALUES (?)", (user_id,))
        else:
            await connection.execute("DELETE FROM waiting_room WHERE user_id=?", (user_id,))
        return await connection.commit()


async def add_fight_room_users(user_id_1, user_id_2):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("INSERT INTO fight_room_users (user_id_1, user_id_2) VALUES (?,?)",
                                 (user_id_1, user_id_2,))
        return await connection.commit()


async def get_fight_room_users(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM fight_room_users WHERE user_id_1 = ? OR user_id_2 = ?",
                                 (user_id, user_id,))
            return await cursor.fetchone()


async def delete_fight_room_users(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("DELETE FROM fight_room_users WHERE user_id_1 = ? OR user_id_2 = ?",
                                 (user_id, user_id,))
        return await connection.commit()


async def set_action_online_fight(user_id, value, action_type, user_position):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            f"UPDATE fight_room_users SET user_{user_position}_{action_type} = ? WHERE user_id_1 = ? OR user_id_2 = ?",
            (value, user_id, user_id,))
        return await connection.commit()


async def set_do_move_online(user_id, value, user_position):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            f"UPDATE fight_room_users SET user_{user_position}_do_move = ? WHERE user_id_1 = ? OR user_id_2 = ?",
            (value, user_id, user_id,))
        return await connection.commit()


async def up_skill_online(user_id, user_position, action_type):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            f"UPDATE fight_room_users SET user_{user_position}_{action_type} = user_{user_position}_{action_type}+1 WHERE user_id_1 = ? OR user_id_2 = ?",
            (user_id, user_id,))
        return await connection.commit()


async def update_move_online(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(f"UPDATE fight_room_users SET move = move + 1 WHERE user_id_1 = ? OR user_id_2 = ?",
                                 (user_id, user_id,))
        return await connection.commit()


async def check_user_in_wait_room(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM waiting_room WHERE user_id=?", (user_id,))
            return bool(await cursor.fetchone())


async def set_random_moves_online(user_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE fight_room_users SET user_1_attack=?, user_2_attack=?, user_1_block=?, user_2_block=? WHERE user_id_1 = ? or user_id_2=?",
                                 (randint(0, 4), randint(0, 4), randint(5, 9), randint(5, 9), user_id, user_id))
        return await connection.commit()


async def set_last_move_time_online(user_id):
    current_time = int(datetime.now().timestamp())
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE fight_room_users SET user_1_last_move_time=?, user_2_last_move_time=? WHERE user_id_1 = ? or user_id_2=?",
                                 (current_time, current_time, user_id, user_id,))
        return await connection.commit()


async def set_losed_actions(user_id, user_position):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute(
            f"UPDATE fight_room_users SET user_{user_position}_attack=777, user_{user_position}_block=777 WHERE user_id_1 = ? or user_id_2=?",
            (user_id, user_id,))
        return await connection.commit()


async def get_clan_war():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM clan_war")
            return await cursor.fetchone()


async def set_clan_war_active():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE clan_war SET is_active=CASE WHEN is_active=1 THEN 0 ELSE 1 END")
        return await connection.commit()


async def set_clan_war_next_war():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE clan_war SET next_war=?", (datetime.now().timestamp() + timedelta(days=config.CLAN_WAR_DAYS_TIME).total_seconds(),))
        return await connection.commit()


async def reset_pvp_points():
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        await connection.execute("UPDATE users SET pvp_points=0")
        return await connection.commit()


async def get_count_keys(nickname: str):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM inventory WHERE item_name=? AND nickname=?",
                                 ("nft_key", nickname,))
            res = await cursor.fetchone()
            return res[0]


async def get_box_loot(box_type):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(f"SELECT item_id FROM resources WHERE item_id LIKE 'nft_{box_type}_%'")
            res = await cursor.fetchall()
            return res + dicts.box_additional_loot[box_type]


async def get_collection(nickname):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                "SELECT DISTINCT item_name FROM inventory WHERE nickname=? AND (item_name LIKE 'nft_epic_box_%' OR item_name LIKE 'nft_siravi_box_%' OR item_name LIKE 'nft_legendary_box_%')",
                (nickname,))
            return await cursor.fetchall()




async def get_dealer_items(item_type, dealer):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            if item_type != "resources":
                dealer_borders = {"centur": [1, 10], "melihor": [11, 20], "nokturn": [21, 32]}
                cur_b = dealer_borders[dealer]
                await cursor.execute(f"SELECT id FROM items WHERE type = '{item_type}' AND {cur_b[0]} <= need_lvl AND need_lvl <= {cur_b[1]}")
                return [item[0] for item in await cursor.fetchall()]

            return dicts.dealer_resources[dealer]



async def get_blacksmith_items_to_craft(city, item_type):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM crafters WHERE city = ? AND type = ?", (city, item_type,))
            return await cursor.fetchall()


async def get_craft(item_id):
    async with aiosqlite.connect(PATH_TO_DB) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM crafters WHERE result = ?", (item_id,))
            return await cursor.fetchone()


#
# async def select_all_items_dict():
#     async with aiosqlite.connect(PATH_TO_DB) as connection:
#         async with connection.cursor() as cursor:
#             await cursor.execute("SELECT * FROM items")
#             res = await cursor.fetchall()
#             var = []
#             for item in res:
#                 var.append({
#                     "id": item[0],
#                     "item_title": item[1],
#                     "item_type": item[2],
#                     "weapon": item[3],
#                     "type": item[4],
#                     "rarity": item[5],
#                     "quality": item[6],
#                     "damage": item[7],
#                     "max_hp": item[8],
#                     "protection": item[9],
#                     "critical": item[10],
#                     "dodge": item[11],
#                     "need_lvl": item[12],
#                     "need_power": item[13],
#                     "need_force": item[14],
#                     "need_intuition": item[15],
#                     "need_dexterity": item[16],
#                     "cost": item[17]
#                 })
#
#         print(var)



# async def insert_toDB():
#     async with aiosqlite.connect(PATH_TO_DB) as connection:
#         for i in var:
#             print(i)
#             await connection.execute("INSERT INTO items "
#                                      "(id, item_title, item_type, rarity, type, quality, damage, max_hp, protection, "
#                                      "critical, dodge, need_lvl, need_power, need_force, need_intuition, need_dexterity, cost) VALUES"
#                                      f"(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
#                                      i['id'], i['item_title'], i['item_type'],  i['rarity'], i["type"], i['quality'],
#                                       i['damage'], i['max_hp'], i['protection'], i['critical'], i['dodge'],
#                                       i['need_lvl'], i['need_power'], i['need_force'], i['need_intuition'],
#                                       i['need_dexterity'], i['cost'],))
#
#         return await connection.commit()
