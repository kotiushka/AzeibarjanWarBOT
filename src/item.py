from AzeibarjanWarBOT.src.dicts import item_haracteristics
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.utils import strings, functions


class InventoryItem:
    def __init__(self, id, item_title, item_type, weapon, rarity, type, quality, damage, health, protect, critical,
                 dodge,
                 need_lvl, need_power, need_force, need_intuition, need_dexterity, cost, description):
        self.id = id
        self.title = item_title
        self.item_type = item_type
        self.weapon = weapon
        self.rarity = rarity
        self.type = type
        self.quality = quality
        self.damage = damage
        self.health = health
        self.protect = protect
        self.critical = critical
        self.dodge = dodge
        self.need_lvl = need_lvl
        self.need_power = need_power
        self.need_force = need_force
        self.need_intuition = need_intuition
        self.need_dexterity = need_dexterity
        self.cost = cost
        self.description = description


    async def get_item_desc(self, need_statistic_bool, user, lvl_up="0", without_cost=False):
        item_bonuses = {"damage": self.damage, "health": self.health, "protect": self.protect,
                        "critical": self.critical, "dodge": self.dodge}

        need_statistic = {"need_lvl": self.need_lvl, "need_power":  self.need_power, "need_force": self.need_force, "need_intuition": self.need_intuition,
                          "need_dexterity": self.need_dexterity}

        lvl_up = "" if str(lvl_up) == "0" else f" (+{lvl_up})"

        item_title = f"<b>{self.title} {lvl_up}</b>\n\n"
        item_type = strings.waepon_info_list[0] + self.item_type + "\n"
        weapon = "" if self.weapon == 0 else strings.waepon_info_list[1] + str(self.weapon) + "\n"
        quality = strings.waepon_info_list[2] + self.quality + "\n"
        rarity = strings.waepon_info_list[3] + self.rarity + "\n\n"
        cost = f'{strings.waepon_info_list[12]}{self.cost}💰'

        item_bonusess = strings.waepon_info_list[4] + "\n"
        item_bstr = "" if self.description is None else f"\n{self.description}\n"
        for i in item_bonuses:
            bonus = item_bonuses[i]
            if bonus != 0:
                item_bstr += item_haracteristics[i] + str(bonus) + lvl_up + "\n"

        if need_statistic_bool:
            item_bstr += "\n"
            item_bstr += strings.waepon_info_list[8] + "\n"
            for i in need_statistic:
                requirement = need_statistic[i]
                if requirement != 0:
                    item_bstr += item_haracteristics[i] + str(await functions.get_lvl_good(requirement)) + await self.get_aviable_value(i, user, need_statistic[i]) + "\n"

        return item_title + item_type + weapon + quality + rarity + item_bonusess + item_bstr + "\n" + (cost if not without_cost else "")


    @staticmethod
    async def get_aviable_value(value, user_info: User, lvl):
        if value == "need_lvl":
            return " 🔻" if user_info.lvl < lvl else ""
        elif value == "need_power":
            return " 🔻" if user_info.power < lvl else ""
        elif value == "need_force":
            return " 🔻" if user_info.force < lvl else ""
        elif value == "need_intuition":
            return " 🔻" if user_info.intuition < lvl else ""
        elif value == "need_dexterity":
            return " 🔻" if user_info.dexterity < lvl else ""

    @property
    def get_item_bonuses(self):
        return [["damage", self.damage], ["max_hp", self.health], ["protection", self.protect],
                ["critical", self.critical], ["dodge", self.dodge]]




