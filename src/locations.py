from datetime import datetime

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.src.clan import Clan
from AzeibarjanWarBOT.src.event import Event
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.utils import strings


class Location:
    def __init__(self, id, name, description, enemy_lvl, need_lvl, aviable_locations):
        self.id = id
        self.name = name
        self.description = description
        self.enemy_lvl = enemy_lvl
        self.need_lvl = need_lvl
        self.aviable_locations = aviable_locations

    async def get_text_city(self, user_info: User):
        event = await DB.get_event()
        cur_event_title = Event(*event).name if event is not None else strings.not_have_event

        text = f"""
<b>{self.name}</b>

{self.description}

{await user_info.get_href_userURL()}
{strings.location_inf[2]} {await DB.get_last_action_in_city(user_info.city)}
{await Location.__get_clan_over_start()}{await self.__get_heirs()}
<b>{strings.event}</b>: {cur_event_title}
️
<a href='t.me/{strings.main_chat}'>{strings.chat_list[0]}</a> | <a href='t.me/{strings.shop_chat}'>{strings.chat_list[1]}</a> | <a href='t.me/{strings.news_chat}'>{strings.chat_list[2]}</a>"""
        return text

    async def get_text_location(self, user_info: User):
        event = await DB.get_event()
        cur_event_title = Event(*event).name if event is not None else strings.not_have_event

        text = f"""
<b>{self.name}</b>

{self.description}

{await user_info.get_href_userURL()}
{strings.location_inf[0]}{self.enemy_lvl}
{strings.location_inf[2]} {await DB.get_last_action_in_city(user_info.city)}
<b>{strings.event}</b>: {cur_event_title}

{strings.down_desc}

<a href='t.me/{strings.main_chat}'>{strings.chat_list[0]}</a> | <a href='t.me/{strings.shop_chat}'>{strings.chat_list[1]}</a> | <a href='t.me/{strings.news_chat}'>{strings.chat_list[2]}</a>
    """
        return text

    @property
    async def get_is_city(self):
        return self.id in strings.city_list


    @staticmethod
    async def __get_clan_over_start():
        clan_war_info = await DB.get_clan_war()
        clan_war_time = datetime.fromtimestamp(clan_war_info[1])
        time_res = ("-".join([str(clan_war_time.year), str(clan_war_time.month), str(clan_war_time.day)]))
        return strings.clan_wars_start_on.format(time_res) if clan_war_info[0] else strings.clan_wars_over_on.format(time_res)


    async def __get_heirs(self):
        try:
            city_position = dicts.clan_winners_positions[self.id]
            heirs = await DB.select_top_info("clan_top")
            cur_clan = Clan(*await DB.get_clan_info_with_clan_id(heirs[city_position][0]))
            return "\n" + strings.heirs.format(await cur_clan.get_clan_title)
        except IndexError:
            return "\n" + strings.heirs.format(strings.empty)
        except KeyError:
            return ""


