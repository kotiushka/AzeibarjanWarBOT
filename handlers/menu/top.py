from datetime import datetime, timedelta

from aiogram import types

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import default
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src.clan import Clan
from AzeibarjanWarBOT.utils import strings


# Рейтинг
@dp.message_handler(IsPrivate(), text=[strings.menuMainButtonsList[6], *strings.top_titles[:-2]])
async def statistics_lvl_and_gold(message: types.Message):

    top_dict = {
        strings.top_titles[0]: [strings.top_titles_in_messages[0], "lvl", message.from_user.id],
        strings.menuMainButtonsList[6]: [strings.top_titles_in_messages[0], "lvl", message.from_user.id],
        strings.top_titles[1]: [strings.top_titles_in_messages[1], "gold", message.from_user.id, False, False, True],
        strings.top_titles[4]: [strings.top_titles_in_messages[2], "glory", message.from_user.id, True],
        strings.top_titles[3]: [strings.top_titles_in_messages[3], "pvp_points", message.from_user.id, False, True],
        strings.top_titles[2]: [strings.top_titles_in_messages[4], "clan_top", message.from_user.id]
    }

    text = await get_list_peoples(*top_dict[message.text])

    await bot.send_message(message.from_user.id, text.format(""), reply_markup=await default.top_buttons())


@dp.message_handler(IsPrivate(), text=strings.top_titles[5])
async def clan_wars_info(message: types.Message):
    clan_war_info = await DB.get_clan_war()
    clan_war_delta = timedelta(seconds=clan_war_info[1] - datetime.now().timestamp())
    days_left = clan_war_delta.days
    hours_left = clan_war_delta.seconds // 3600
    minutes_left = (clan_war_delta.seconds // 60) % 60

    clan_war_action = strings.clan_war_is_will_be_started if not clan_war_info[0] else strings.clan_war_is_will_be_over
    text = await get_list_peoples(strings.top_titles[5], "clan_top", message.from_user.id)
    await bot.send_message(message.from_user.id, text.format(
        strings.clan_war_will_be_x.format(clan_war_action, days_left, hours_left, minutes_left)))



async def get_list_peoples(title_text, value, user_id, glory=False, pvp_points=False, gold=False):
    top_info = await DB.select_top_info(value)
    text = [f"<b>{title_text}</b>" + "\n" + f"{'{}' if value == 'clan_top' else ''}"]
    index = 1
    for i in top_info[:30]:
        if value != "clan_top":
            default_text = f"{index}. {strings.courses[i[2]][0]} <a href='tg://user?id={i[0]}'>{i[1]}</a> 🔸️{i[3]} "
            if glory:
                default_text += f"🏵 {i[4]}"
            if pvp_points:
                default_text += f"♨️ {i[5]}"
            if gold:
                default_text += f"💰 {i[6]}"
            text.append(default_text)
        else:
            clan_info = Clan(*await DB.get_clan_info_with_clan_id(i[0]))
            text.append(
                f"{index}. " + await clan_info.get_clan_title + f": ♨️ {i[1]} {'🏆' if index in [1, 2, 3] else ''}")

        index += 1

    res = "\n".join(text) + "\n\n"
    return res + await get_your_position_in_top(top_info, user_id) if value != "clan_top" else res

async def get_your_position_in_top(top: list[tuple], user_id) -> str:
    index = 1
    for i in top:
        if i[0] == user_id:
            return f"{strings.your_rate} <b>{index}</b>"
        index += 1



