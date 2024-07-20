import random
from random import randint

from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.src.enemy import Enemy
from AzeibarjanWarBOT.src.trick import Trick
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.utils import strings


class Fight:
    def __init__(self, move, user_id, enemy_id, enemy_current_hp, attacks, user_attack, user_block, dext,
                 user_last_trick, used_tricks, npc_block, npc_attack, can_do_move, last_move_time):
        self.__move = move
        self.__user_id = user_id
        self.__enemy_id = enemy_id
        self.__enemy_current_hp = enemy_current_hp
        self.__attacks = attacks
        self.__user_attack = user_attack
        self.__user_block = user_block
        self.__dext = dext
        self.__user_last_trick = user_last_trick
        self.__used_tricks = used_tricks
        self.__npc_block = npc_block
        self.__npc_attack = npc_attack
        self.can_do_move = can_do_move
        self.last_move_time = last_move_time

    async def __get_text_move_user(self, is_losed=False):
        is_critical = False
        current_trick = await self.get_user_last_trick
        if current_trick is not None:
            res = await current_trick.use_trick()
            is_critical = True if res["critical"] else False

        # Получим get_text_blocked
        text_move = await self.__get_text_blocked_user(is_losed)
        # Если get_text_blocked выдал False (действие не было заблокировано)
        if text_move is False:
            # Если выпадет то сработает крит урон
            if randint(config.CRITICAL_DAMAGE_CHANCE[0], config.CRITICAL_DAMAGE_CHANCE[1]) == \
                    config.CRITICAL_DAMAGE_CHANCE[0] or is_critical:
                # Получим характеристики юзера
                user_info = User(*await DB.get_user_info(self.__user_id))
                user_haracteristics = await user_info.get_aviable_haracteristics()
                # Если критический урон в характеристиках != 0, в противном случае крит сработать не может
                if user_haracteristics[2] != 0:
                    return await self.__get_text_critical_user()
                return await self.__get_text_default_attack_user()
            # Если удар выпал не критический
            return await self.__get_text_default_attack_user()
        # Если удар был заблокирован
        else:
            return text_move

    async def __get_text_move_npc(self, blocked_user: bool):
        # Получим get_text_blocked
        text_move = await self.__get_text_blocked_npc(blocked_user)
        # Если get_text_blocked выдал False (действие не было заблокировано)
        if text_move is False:
            # Если выпадет то сработает крит урон
            if randint(config.CRITICAL_DAMAGE_CHANCE[0], config.CRITICAL_DAMAGE_CHANCE[1]) == \
                    config.CRITICAL_DAMAGE_CHANCE[0]:
                return await self.__get_text_critical_npc()
            # Если удар выпал не критический
            return await self.__get_text_default_attack_npc()
        # Если удар был заблокирован
        else:
            return text_move

    async def __get_text_blocked_user(self, is_losed=False):
        """
        Функция для получения инфы об блоке юзера
        :return: False если действие не было заблокировано, str с описанием что блокировано было в противном случае.
        """
        block = await DB.get_npc_actions_fight_room(self.__user_id)
        block = block[1]

        blocked = await strings.is_block(self.__user_attack, block, "user", is_losed)

        current_trick = await self.get_user_last_trick
        if current_trick is not None:
            res = await current_trick.use_trick()
            if res["health"] != 0:
                user_info = User(*await DB.get_user_info(self.__user_id))
                user_haracteristics = await user_info.get_aviable_haracteristics()
                hp_info = await DB.get_hp(self.__user_id)
                if hp_info[0] + res["health"] > user_haracteristics[0]:
                    await DB.set_current_hp(self.__user_id, user_haracteristics[0] - hp_info[0])
                else:
                    await DB.set_current_hp(self.__user_id, res["health"])
            return False

        if blocked == "lose_time":
            return strings.fight_info[6] + "\n\n\n"
        elif blocked:
            return f"{strings.fight_info[1]} <b>{strings.fight_actions_buttons[self.__user_attack].lower()}.</b> " + \
                strings.fight_info[2] + "\n\n\n"
        return False

    async def __get_text_blocked_npc(self, is_blocked_user: bool):
        """
        Функция для получения инфы об блоке нпс
        :return: False если действие не было заблокировано, str с описанием что блокировано было в противном случае.
        """
        actions = await DB.get_npc_actions_fight_room(self.__user_id)
        action_attack = actions[0]
        action_block = self.__user_block

        blocked = await strings.is_block(action_attack, action_block, "npc", is_blocked_user)

        if blocked:
            await self.up_dext()
            return f"{strings.fight_info[1]} <b>{strings.fight_actions_buttons[action_attack].lower()}.</b> " + \
                strings.fight_info[2] + "\n\n\n"

        return False

    async def __get_text_default_attack_user(self):
        text_move = f"{strings.fight_info[1]} <b>{strings.fight_actions_buttons[self.__user_attack].lower()}.</b> "
        await self.up_attack()
        user_info = User(*await DB.get_user_info(self.__user_id))
        user_haracteristics = await user_info.get_aviable_haracteristics()
        damage = user_haracteristics[1] - randint(0, user_haracteristics[1] // 5)

        current_trick = await self.get_user_last_trick
        if current_trick is not None:
            res = await current_trick.use_trick()
            damage = res["user_1_attack"]

        await self.set_enemy_hp(damage)

        return text_move + " " + strings.fight_info[3] + f"<b>{damage}</b> " + strings.fight_info[4] + "\n\n\n"

    async def __get_text_default_attack_npc(self):
        text_move = f"{strings.fight_info[1]} <b>{strings.fight_actions_buttons[self.__user_attack].lower()}.</b> "
        enemy_info = await DB.get_enemy(self.__enemy_id)
        user_info = User(*await DB.get_user_info(self.__user_id))
        user_haracteristics = await user_info.get_aviable_haracteristics()
        damage = max(randint(enemy_info.min_damage, enemy_info.max_damage) - user_info.protection, 0)

        dodged = randint(config.DODGE_CHANCE[0], config.DODGE_CHANCE[1]) == 1
        if dodged:
            if user_haracteristics[3]:
                damage = max(damage - user_haracteristics[3], 0)

        current_trick = await self.get_user_last_trick
        if current_trick is not None:
            res = await current_trick.use_trick()
            damage = res["user_2_attack"]

        await self.set_user_hp(damage)

        return text_move + " " + strings.fight_info[3] + f"<b>{damage}</b> " + strings.fight_info[
            4] + (strings.opponent_use_dodge.format(user_haracteristics[3]) if dodged and user_haracteristics[3] else "") + "\n\n\n"

    async def __get_text_critical_user(self):
        text_move = f"{strings.fight_info[1]} <b>{strings.fight_actions_buttons[self.__user_attack].lower()}.</b> "

        await self.up_attack()
        user_info = User(*await DB.get_user_info(self.__user_id))
        user_haracteristics = await user_info.get_aviable_haracteristics()

        damage = (user_haracteristics[1] - randint(0, user_haracteristics[1] // 5)) + user_haracteristics[2]
        current_trick = await self.get_user_last_trick
        if current_trick is not None:
            res = await current_trick.use_trick()
            damage = res["user_1_attack"]

        await self.set_enemy_hp(damage)

        return text_move + strings.fight_info[3] + strings.fight_info[5] + f"<b>{damage}</b> " + strings.fight_info[
            4] + "\n\n\n"

    async def __get_text_critical_npc(self):
        actions = await DB.get_npc_actions_fight_room(self.__user_id)

        text_move = f"{strings.fight_info[1]} <b>{strings.fight_actions_buttons[actions[0]].lower()}.</b> "
        enemy_info = await DB.get_enemy(self.__enemy_id)

        user_info = User(*await DB.get_user_info(self.__user_id))
        user_haracteristics = await user_info.get_aviable_haracteristics()

        global_damage = randint(enemy_info.min_damage, enemy_info.max_damage)
        global_damage = max(round(global_damage * random.choice([1.3, 1.4, 1.5])) - user_info.protection, 0)

        dodged = randint(config.DODGE_CHANCE[0], config.DODGE_CHANCE[1]) == 1
        if dodged:
            if user_haracteristics[3]:
                global_damage = max(global_damage - user_haracteristics[3], 0)

        current_trick = await self.get_user_last_trick
        if current_trick is not None:
            res = await current_trick.use_trick()
            global_damage = res["user_2_attack"]

        await self.set_user_hp(global_damage)

        return text_move + strings.fight_info[3] + strings.fight_info[5] + f"<b>{global_damage}</b> " + (
            strings.fight_info[4] + strings.opponent_use_dodge.format(user_haracteristics[3]) if dodged and
                                                                                                 user_haracteristics[
                                                                                                     3] else "") + "\n\n\n"

    async def get_text_fight(self, is_losed=False):
        # Создание переменных, которые отвечают за атаку и блок бота
        await DB.set_attack_action(self.__user_id, randint(5, 9), "block", "npc")
        await DB.set_attack_action(self.__user_id, randint(0, 4), "attack", "npc")

        enemy_info = await DB.get_enemy(self.__enemy_id)
        user_text = await self.__get_text_move_user(is_losed)
        npc_text = await self.__get_text_move_npc(is_losed)

        user_info = User(*await DB.get_user_info(self.__user_id))

        combination_text = await self.get_use_combination_text()
        await DB.update_move(self.__user_id)
        await DB.clear_last_trick(self.__user_id)

        return f"{strings.fight_info[0]} {self.__move}\n\n" \
               f"{combination_text}{'🕓 ' if is_losed else ''}{await user_info.get_href_userURL()} {user_text} " \
               f"<b>{enemy_info.name}</b> ⭐{enemy_info.lvl} ❤ ({await self.get_enemy_current_hp}/{enemy_info.max_hp}) {npc_text}" \
               f"🗡{await DB.get_skill(self.__user_id, 'attacks')} 🛡️ {await DB.get_skill(self.__user_id, 'dext')}"

    async def up_attack(self):
        return await DB.up_skill(self.__user_id, "attacks")

    async def up_dext(self):
        return await DB.up_skill(self.__user_id, "dext")

    async def set_user_hp(self, damage):
        return await DB.set_current_hp(self.__user_id, damage, "-")

    async def set_enemy_hp(self, damage):
        return await DB.set_enemy_current_hp(self.__user_id, damage)

    @property
    async def get_enemy(self) -> Enemy:
        return await DB.get_enemy(self.__enemy_id)

    @property
    async def get_enemy_current_hp(self):
        res = await DB.get_enemy_current_hp(self.__user_id)
        if res < 0:
            return 0
        return res

    async def attack_and_block(self, user_id=None):
        return [self.__attacks, self.__dext]

    @property
    async def get_user_last_trick(self):
        return None if self.__user_last_trick is None else Trick(*await DB.get_trick(self.__user_last_trick))

    async def get_used_tricks(self, user_id=None):
        return self.__used_tricks.split() if self.__used_tricks is not None else []

    async def get_use_combination_text(self):
        last_trick = await self.get_user_last_trick
        if last_trick is not None:
            user_info = User(*await DB.get_user_info(self.__user_id))
            text = await user_info.get_href_userURL()
            text = " ".join(text.split()[:-1])
            return text + strings.use_trick_round_text + f"<b>{last_trick.title}</b>\n<code>{last_trick.description}</code>\n\n"
        return ""
