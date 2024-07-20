from AzeibarjanWarBOT.src.dicts import item_haracteristics
from AzeibarjanWarBOT.src.item import InventoryItem
from AzeibarjanWarBOT.utils import strings


class Trick:

    def __init__(self, id, title, description, need_lvl, need_power, need_force, need_intuition, need_dexterity, cost,
                 repeat, need_round_attack, need_round_block, user_1_attack, user_2_attack, health, critical):
        self.id = id
        self.title = title
        self.description = description
        self.need_lvl = need_lvl
        self.need_power = need_power
        self.need_force = need_force
        self.need_intuition = need_intuition
        self.need_dexterity = need_dexterity
        self.cost = cost
        self.type = "trick"
        self.repeat = repeat
        self.need_round_attack = need_round_attack
        self.need_round_block = need_round_block
        self.user_1_attack = user_1_attack
        self.user_2_attack = user_2_attack
        self.health = health
        self.critical = bool(critical)

    async def get_item_desc_dealer(self, user, npc):

        need_statistic = {"need_lvl": self.need_lvl, "need_power": self.need_power, "need_force": self.need_force,
                          "need_intuition": self.need_intuition,
                          "need_dexterity": self.need_dexterity}

        text = f"{npc}\n\n<b>{self.title}:</b>\n\n<i>{self.description}</i>\n\n{strings.req}\n"

        for i in need_statistic:
            requirement = need_statistic[i]
            if requirement != 0:
                text += item_haracteristics[i] + str(requirement) + await InventoryItem.get_aviable_value(i, user,
                                                                                                          need_statistic[
                                                                                                              i]) + "\n"
        return text + f'\n{strings.waepon_info_list[12]}{self.cost}💰\n\n'

    async def get_item_desc_tricks(self, user, use):
        need_statistic = {"need_lvl": self.need_lvl, "need_power": self.need_power, "need_force": self.need_force,
                          "need_intuition": self.need_intuition,
                          "need_dexterity": self.need_dexterity}

        text = f"<b>{self.title}</b>\n<code>{self.description}</code>\n{strings.req}\n"
        for i in need_statistic:
            requirement = need_statistic[i]
            if requirement != 0:
                text += f"<b>{item_haracteristics[i]} {str(requirement)}</b>" + await InventoryItem.get_aviable_value(i,
                                                                                                                      user,
                                                                                                                      need_statistic[
                                                                                                                          i]) + "\n"

        text += f"Можно использовать: {'✅' if use == True else '❌'}"

        return text + "\n"

    @property
    async def get_need_round_items(self):
        return [self.need_round_attack, self.need_round_block]

    async def use_trick(self) -> dict:
        return await Trick.get_trick_dict(self.user_1_attack, round(23 - (23 * (self.user_2_attack / 100))), self.health, self.critical)

    @staticmethod
    async def get_trick_dict(user_1_attack: int, user_2_attack: int, health: int, crit: bool) -> dict:
        return {
            "user_1_attack": user_1_attack,
            "user_2_attack": user_2_attack,
            "health": health,
            "critical": crit
        }


