import datetime
from random import randint

from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.src.trick import Trick
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.utils import strings


class FightRoomUsers:
    def __init__(self, move, user_id_1, user_id_2, user_1_attacks, user_2_attacks, user_1_blocks,
                 user_2_blocks, user_1_do_move, user_2_do_move, user_1_attack, user_2_attack, user_1_block,
                 user_2_block, user_1_tricks, user_2_tricks, user_1_last_trick, user_2_last_trick,
                 user_1_last_move_time,
                 user_2_last_move_time):

        self.move = move

        self.user_id_1 = user_id_1
        self.user_id_2 = user_id_2

        self.user_1_attacks = user_1_attacks
        self.user_1_blocks = user_1_blocks
        self.user_2_attacks = user_2_attacks
        self.user_2_blocks = user_2_blocks

        self.user_1_do_move = user_1_do_move
        self.user_2_do_move = user_2_do_move

        self.user_1_attack = user_1_attack
        self.user_1_block = user_1_block
        self.user_2_attack = user_2_attack
        self.user_2_block = user_2_block

        self.user_1_tricks = user_1_tricks
        self.user_2_tricks = user_2_tricks

        self.user_1_last_trick = user_1_last_trick
        self.user_2_last_trick = user_2_last_trick

        self.user_1_last_move_time = user_1_last_move_time
        self.user_2_last_move_time = user_2_last_move_time

    async def get_another_player(self, user_id, is_position=False):
        if self.user_id_1 == user_id:
            return self.user_id_2 if not is_position else 1
        return self.user_id_1 if not is_position else 2

    async def get_player_position(self, user_id):
        return 1 if self.user_id_1 == user_id else 2

    async def increase_glory_pvp_points(self, winner):
        clan_war_info = await DB.get_clan_war()

        if self.user_id_1 == winner:
            user_id_winner, user_id_loser = self.user_id_1, self.user_id_2
        else:
            user_id_winner, user_id_loser = self.user_id_2, self.user_id_1

        await DB.update_glory(config.GLORY_REWARD_ONLINE, "+", user_id_winner)
        await DB.update_glory(config.GLORY_DISCARD_ONLINE, "-", user_id_loser)

        if clan_war_info[0]:
            await DB.update_glory(config.PVP_POINTS_DISCARD_ONLINE, "-", user_id_loser, column_type="pvp_points")
            await DB.update_glory(config.PVP_POINTS_REWARD_ONLINE, "+", user_id_winner, column_type="pvp_points")

    async def round_resultat(self, user_1_losed=False, user_2_losed=False, text=""):
        position_user_id_1 = await self.get_another_player(self.user_id_1, True)
        position_user_id_2 = await self.get_another_player(self.user_id_2, True)
        stats = \
            [
                {"id": self.user_id_1, "attack": self.user_1_attack, "block": self.user_2_block,
                 "is_losed": user_1_losed if position_user_id_1 == 1 else user_2_losed, "opponent_id": self.user_id_2},
                {"id": self.user_id_2, "attack": self.user_2_attack, "block": self.user_1_block,
                 "is_losed": user_2_losed if position_user_id_2 == 2 else user_1_losed, "opponent_id": self.user_id_1}
            ]

        resultat = {}
        await DB.update_move_online(self.user_id_1)
        for user in stats:
            user_position = await self.get_player_position(user['id'])
            user_info = User(*await DB.get_user_info(user["id"]))

            opponent_info = User(*await DB.get_user_info(user["opponent_id"]))

            # Если пользователь не пропустил удар
            if not user["is_losed"]:
                # Если противник не заблокировал удар
                if not user["block"] in dicts.block_variants[user["attack"]]:
                    await DB.up_skill_online(user["id"], user_position, "attacks")
                    user_haracteristics = await user_info.get_aviable_haracteristics()

                    is_dodged = randint(config.DODGE_CHANCE[0], config.DODGE_CHANCE[1]) == config.DODGE_CHANCE[0]

                    # Если выпадет то сработает крит урон
                    if randint(config.CRITICAL_DAMAGE_CHANCE[0], config.CRITICAL_DAMAGE_CHANCE[1]) == config.CRITICAL_DAMAGE_CHANCE[0] and \
                            user_haracteristics[2] != 0:
                        damage = max(user_haracteristics[1] - randint(0, user_haracteristics[1] // 5) + user_haracteristics[2] - opponent_info.protection, 0)
                        res = await self.resultat_with_trick(damage, user, is_cricital=True, is_dodged=is_dodged)
                    else:
                        damage = max(user_haracteristics[1] - randint(0, user_haracteristics[1] // 5) - opponent_info.protection, 0)
                        res = await self.resultat_with_trick(damage, user, is_dodged=is_dodged)

                    resultat[f"user_{user_position}"] = res

                # Если противник заблокировал удар
                else:
                    opponent_position = 1 if user_position == 2 else 2
                    await DB.up_skill_online(user["opponent_id"], opponent_position, "blocks")
                    resultat[f"user_{user_position}"] = await self.resultat_with_trick(0, user, is_blocked=True)

            # Если пользователь пропустил удар
            else:
                user_info = User(*await DB.get_user_info(user["id"]))
                resultat[f"user_{user_position}"] = f"🕓 {await user_info.get_href_userURL()} {strings.fight_info[6]}"

        fight_info = FightRoomUsers(*await DB.get_fight_room_users(self.user_id_1))

        user_info_1 = User(*await DB.get_user_info(self.user_id_1))
        user_info_2 = User(*await DB.get_user_info(self.user_id_2))
        text = "" if text == "" else text + "\n\n"
        await DB.set_last_move_time_online(self.user_id_1)
        return f"{strings.fight_info[0]} {fight_info.move}\n\n" \
               f"{text}" \
               f"{resultat['user_1'].format(await user_info_1.get_href_userURL(), await user_info_1.get_href_userURL())}\n" \
               f"🗡{fight_info.user_1_attacks} 🛡️ {fight_info.user_1_blocks}\n\n" \
               f"{resultat['user_2'].format(await user_info_2.get_href_userURL(), await user_info_2.get_href_userURL())}\n" \
               f"🗡{fight_info.user_2_attacks} 🛡️ {fight_info.user_2_blocks}"

    async def get_used_tricks(self, user_id):
        if user_id == self.user_id_1:
            return self.user_1_tricks.split() if self.user_1_tricks is not None else []
        return self.user_2_tricks.split() if self.user_2_tricks is not None else []

    async def attack_and_block(self, user_id=None):
        if user_id == self.user_id_1:
            return [self.user_1_attacks, self.user_1_blocks]
        return [self.user_2_attacks, self.user_2_blocks]

    async def get_user_last_trick(self, position):
        if position == 1:
            return None if self.user_1_last_trick is None else Trick(*await DB.get_trick(self.user_1_last_trick))
        return None if self.user_2_last_trick is None else Trick(*await DB.get_trick(self.user_2_last_trick))

    async def resultat_with_trick(self, damage: int, user: dict, is_cricital=False, is_blocked=False, is_dodged=False):
        user_position = await self.get_player_position(user["id"])

        await DB.clear_last_trick(user["id"], user_position)

        user_info = User(*await DB.get_user_info(user["id"]))
        opponent_info = User(*await DB.get_user_info(user["opponent_id"]))

        user_haracteristics = await user_info.get_aviable_haracteristics()
        opponent_haracteristics = await opponent_info.get_aviable_haracteristics()

        damage = await self.get_user_damage_with_opponent_trick(user_position, damage)

        user_last_trick = await self.get_user_last_trick(user_position)
        if user_last_trick is None:
            if is_dodged:
                damage = max(damage - opponent_haracteristics[3], 0)

            default_string_start = f"{strings.fight_info[1]} {strings.fight_actions_buttons[user['attack']].lower()} "
            if not is_cricital and not is_blocked:
                resultat = f"{{}} {default_string_start} {strings.fight_info[3]}{damage} {strings.fight_info[4]}. "
            elif is_cricital:
                resultat = f"{{}} {default_string_start} {strings.fight_info[3]}{strings.fight_info[5]} {damage} {strings.fight_info[4]}. "
            else:
                resultat = f"{{}} {default_string_start} {strings.fight_info[2]}. "

            if is_dodged:
                if opponent_haracteristics[3]:
                    resultat += strings.opponent_use_dodge.format(opponent_haracteristics[3])


        else:
            trick_dict_info = await user_last_trick.use_trick()

            if trick_dict_info["health"]:
                await DB.set_current_hp(user["id"], trick_dict_info["health"], max_hp=user_haracteristics[0])

            damage = await self.get_user_damage_with_opponent_trick(user_position, trick_dict_info["user_1_attack"])
            resultat = await self.get_full_text_with_trick(user_last_trick, user, damage, trick_dict_info["critical"])

        await DB.set_current_hp(user['opponent_id'], damage, "-")

        return resultat

    async def get_user_damage_with_opponent_trick(self, user_position, damage):
        user_last_trick = await self.get_user_last_trick(2 if user_position == 1 else 1)
        if user_last_trick is not None:
            trick_dict_info = await user_last_trick.use_trick()
            return trick_dict_info["user_2_attack"]
        return damage

    @staticmethod
    async def get_full_text_with_trick(user_last_trick: Trick, user: dict, damage, is_critical=False):
        last_string = f" {strings.fight_info[3]} {strings.fight_info[5]}{damage} {strings.fight_info[4]}" if is_critical else f"{strings.fight_info[3]}{damage} {strings.fight_info[4]}"
        return \
            f"{strings.use_trick.format('{}', user_last_trick.title, user_last_trick.description)} " \
            f"{{}} {strings.fight_info[1]} {strings.fight_actions_buttons[user['attack']].lower()}. {last_string}"

    async def check_time(self, is_full, user_id):
        check_time = self.user_1_last_move_time if user_id == self.user_id_1 else self.user_2_last_move_time
        time_value = config.MOVE_TIME_ONLINE if is_full else config.MOVE_TIME_ONLINE // 2
        return time_value <= datetime.datetime.now().timestamp() - check_time <= time_value+3

