from AzeibarjanWarBOT.utils import strings, functions


class User:
    def __init__(self, id, username, nickname, course, city, current_hp, max_hp, gold, coupon, current_xp, glory, stat_point,
                 bonus_xp, bonus_gold, damage, protection, critical, dodge, force, power, dexterity, intuition, lvl,
                 weapon, helmet, armor, gloves, boots, shield, ring, necklace, accessory, healing, trick_1, trick_2,
                 trick_3, pvp_points, clan, clan_invite_join, clan_invites, last_action, regen_hp, current_potions, referals, event_reward):
        self.id = id
        self.username = username
        self.nickname = nickname
        self.course = course
        self.city = city
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.gold = gold
        self.coupon = coupon
        self.current_xp = current_xp
        self.glory = glory
        self.stat_point = stat_point
        self.bonus_xp = bonus_xp
        self.bonus_gold = bonus_gold
        self.damage = damage
        self.protection = protection
        self.critical = critical
        self.dodge = dodge
        self.force = force
        self.power = power
        self.dexterity = dexterity
        self.intuition = intuition
        self.lvl = lvl
        self.weapon = weapon
        self.helmet = helmet
        self.armor = armor
        self.gloves = gloves
        self.boots = boots
        self.shield = shield
        self.ring = ring
        self.necklace = necklace
        self.accessory = accessory
        self.healing = healing
        self.trick_1 = trick_1
        self.trick_2 = trick_2
        self.trick_3 = trick_3
        self.pvp_points = pvp_points
        self.clan = clan
        self.clan_invite_join: str = clan_invite_join
        self.clan_invites: str = clan_invites
        self.last_action = last_action
        self.regen_hp = regen_hp
        self.current_potions = current_potions.split()
        self.referals = referals
        self.event_reward = event_reward

    @property
    def get_tricks(self):
        return [self.trick_1, self.trick_2, self.trick_3]

    @property
    def get_arr_atr(self):
        return [self.power, self.force, self.dexterity, self.intuition, self.stat_point]

    @property
    def get_user_weap_arr(self) -> list[str]:
        return [self.weapon, self.helmet, self.armor, self.gloves, self.boots, self.shield, self.ring,
                self.necklace, self.accessory]

    async def get_aviable_haracteristics(self):
        return [self.max_hp + (self.force * 15), self.damage + (self.power * 3),
                self.critical + (self.intuition * 7),
                self.dodge + (self.dexterity * 7)]

    async def get_href_userURL(self):
        from AzeibarjanWarBOT.database import DB

        haracteristics = await self.get_aviable_haracteristics()
        try:
            user_clan = await DB.get_user_clan(self.id)
            clan_emoji = await DB.get_clan_emoji(user_clan[2])
        except TypeError:
            clan_emoji = ""
        return f"{clan_emoji}{strings.courses[self.course][0]} <a href='tg://user?id={self.id}'>{self.nickname}</a> ⭐{await functions.get_lvl_good(self.lvl)} ❤({self.current_hp}/{haracteristics[0]})"

    async def get_href_without_hp(self):
        from AzeibarjanWarBOT.database import DB
        try:
            user_clan = await DB.get_user_clan(self.id)
            clan_emoji = await DB.get_clan_emoji(user_clan[2])
        except TypeError:
            clan_emoji = ""

        return f"{clan_emoji}{strings.courses[self.course][0]} <a href='tg://user?id={self.id}'>{self.nickname}</a> ⭐{await functions.get_lvl_good(self.lvl)}"

    async def get_glory_rank(self):
        glory_limits = [0, 25, 50, 75, 100, 140, 170, 200, 250, 300, 350, 400, 500]
        if self.glory >= 500:
            return strings.glory_rank_list[-1]

        index = glory_limits.index(next(filter(lambda x: x > self.glory, glory_limits), glory_limits[-1]))
        return strings.glory_rank_list[index - 1]

    @property
    async def get_clan_invites(self):
        return list(map(int, self.clan_invites.split())) if self.clan_invites is not None else None

    @property
    async def get_user_description(self):
        return f"{strings.user_desc_attrs[0].format(await self.get_href_without_hp())}\n\n" \
               f"{strings.user_desc_attrs[1].format(await functions.get_lvl_good(self.lvl))}\n" \
               f"{strings.user_desc_attrs[2].format(self.pvp_points)}\n" \
               f"{strings.user_desc_attrs[3].format(self.glory, await self.get_glory_rank())}"

    @property
    async def get_collection(self):
        from AzeibarjanWarBOT.database import DB
        from AzeibarjanWarBOT.utils.class_getter import get_resource
        user_collection = await DB.get_collection(self.nickname)
        res = ""
        for nft in user_collection:
            cur_nft_res = await get_resource(nft[0])
            nft_emoji = cur_nft_res.title.split("-")[0]
            res += nft_emoji

        return strings.empty if not res else res




