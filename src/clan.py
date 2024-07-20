from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.utils import strings


class Clan:
    def __init__(self, id, name, current_emoji, aviable_emojies):
        self.id = id
        self.name = name
        self.current_emoji = current_emoji
        self.aviable_emojies = aviable_emojies

    async def get_clan_text(self):
        return f"{strings.clan_list_actions[0].format(self.name)}\n" \
               f"{await self.get_clan_users_count()}" \
               f"{await self.get_clan_leader_text}" \
               f"{strings.clan_list_actions[3].format(self.id)}"

    @property
    async def get_clan_description(self):
        return f"{strings.menuMainButtonsList[3]}\n\n" \
               f"{await self.get_clan_title}\n\n" \
               f"{strings.sostav.format(await self.get_clan_users_count(True), config.CLAN_USERS_COUNT)}\n" \
               f"{await self.get_clan_leader_text}" \
               f"{await self.get_clan_power}\n" \
               f"{strings.pre_heads.format(await self.get_pre_heads)}\n"

    @property
    async def get_pre_heads(self):
        resultat = []
        for pre_head in await DB.get_pre_heads(self.id):
            user_info = User(*await DB.get_user_info(pre_head[0]))
            resultat.append(await user_info.get_href_without_hp())

        return ", ".join(resultat) if resultat else strings.empty

    @property
    async def get_clan_emoji(self):
        return await DB.get_clan_emoji(self.current_emoji)

    @property
    async def get_clan_leader_text(self):
        clan_leader = User(*await DB.get_user_info(await DB.get_clan_leader(self.id)))
        return f"{strings.clan_list_actions[2].format(await clan_leader.get_href_without_hp())}\n"

    async def get_clan_users_count(self, only_num=False):
        users_count = await DB.get_clan_users_count_with_clan_id(self.id)
        return f"{strings.clan_list_actions[1].format(users_count)}\n" if not only_num else users_count

    @property
    async def get_clan_power(self):
        return strings.clan_power.format(await DB.get_pvp_points_clan(self.id))

    @property
    async def get_clan_title(self):
        return f"{await self.get_clan_emoji} {self.name}"


    @property
    async def get_aviable_emojies(self):
        return list(map(int, self.aviable_emojies.split()))

