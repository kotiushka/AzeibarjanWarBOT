import hashlib
import random

from aiogram import types
from aiogram.types import InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardMarkup, InlineKeyboardButton

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.src.clan import Clan
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_item, get_resource, get_trick, get_user_info, get_clan_info


@dp.inline_handler()
async def inline_handler(inline_query: types.InlineQuery):
    offset = int(inline_query.offset) if inline_query.offset else 0
    querry_text = inline_query.query.strip()

    querry_params = " ".join(querry_text.split()[2:])
    query_param_text = " ".join(querry_text.split(" ")[:2]) + " "

    try:
        items = await __get_inline_array(dicts.querry_variants[query_param_text], querry_params)
        items = items[offset:offset + 50]

        if len(items) == 0:
            return

        await bot.answer_inline_query(inline_query.id, results=items, cache_time=0, next_offset=offset + 50)

    except (KeyError, TypeError) as ex:
        print(ex)


async def __get_inline_array(value, querry_params: str):
    if value == "clan_users":
        try:
            array_items = await DB.select_clan_users(querry_params)
        except ValueError:
            return
    elif value == "clans":
        array_items = await DB.select_all_clans(querry_params)

    else:
        array_items = await DB.select_all_items(value, querry_params, dicts.names_inline_array_types[value])


    if value == "opponents":
        return [await __get_input_text_content(i[1], f"🔸{i[3]}\n🗺{dicts.transitions_v2[i[7]]}", f"/getmob {i[0]}") for i in
                array_items]
    elif value == "items":
        return [await __get_input_text_content(i[1], f"{strings.rarity} {i[4]}", f"/getequip {i[0]}") for i in
                array_items]
    elif value == "resources":
        return [await __get_input_text_content(i[2], i[5], f"/getasset {i[1]}") for i in array_items]
    elif value == "tricks":
        return [await __get_input_text_content(i[1], i[2], f"/getcombo {i[0]}") for i in array_items]
    elif value == "users" or value == "clan_users":
        res = []
        for i in array_items:
            user_info = await get_user_info(i[0] if value == "users" else i[1])
            res.append(await __get_input_text_content(f"{strings.courses[user_info.course][0]} {user_info.nickname}", f"🔸 {user_info.lvl}\n{strings.user_power.format(user_info.pvp_points)}", f"/{'getuser' if value == 'users' else 'getclanuser'} {user_info.id}"))
        return res
    elif value == "clans":
        res = []
        for clan in array_items:
            clan_info = Clan(*await DB.get_clan_info_with_clan_id(clan[0]))
            res.append(await __get_input_text_content(f"{await clan_info.get_clan_emoji} {clan[1]}", f"{strings.players.format(clan[2])}", f"/get_clan {clan[0]}"))
        return res





async def __get_input_text_content(title: str, description: str,
                                   input_message_content: str) -> InlineQueryResultArticle:
    item = InlineQueryResultArticle(
        id=hashlib.md5(str(random.randint(10000000, 999999999)).encode()).hexdigest(),
        title=title,
        description=description,
        input_message_content=InputTextMessageContent(input_message_content)
    )
    return item


@dp.message_handler(IsPrivate(), commands=["getmob", "getequip", "getasset", "getcombo", "getuser", "get_clan"])
async def get_mob_desc(message: types.Message):
    try:
        reply_markup = None
        command_info = message.text.split()
        if len(command_info) == 2:
            command = command_info[0][1:]
            arg = command_info[1]
            user_info = await get_user_info(message.from_user.id)

            if command == "getmob":
                enemy_info = await DB.get_enemy(arg)
                text = strings.mob_desc_main_word[0] + await enemy_info.get_enemy_desc

            elif command == "getequip":
                item_info = await get_item(arg)
                text = strings.mob_desc_main_word[1] + await item_info.get_item_desc(True, user_info)

            elif command == "getasset":
                resource_info = await get_resource(arg)
                text = f"{strings.mob_desc_main_word[2]}"
                if resource_info.type == "recepie":
                    text += await resource_info.crafter_description()
                elif resource_info.type == "potion":
                    text += await resource_info.potion_description()
                else:
                    text += await resource_info.default_description()

            elif command == "getcombo":
                trick_info = await get_trick(arg)
                text = strings.mob_desc_main_word[3] + await trick_info.get_item_desc_tricks(user_info, True)

            elif command == "getuser":
                user_info_main_player = await get_user_info(message.from_user.id)
                user_info = await get_user_info(arg)

                if user_info.city == user_info_main_player.city and user_info.id != user_info_main_player.id:
                    reply_markup = await inline.send_trade(arg)
                if await have_acces(message.from_user.id) and user_info.id != user_info_main_player.id:
                    keyb_inv = InlineKeyboardButton(text=strings.clan_invite, callback_data=f"send_invite-{user_info.id}")
                    if reply_markup is None:
                        reply_markup = InlineKeyboardMarkup(resize_keyboard=True).add(keyb_inv)
                    else:
                        reply_markup = reply_markup.add(keyb_inv)


                text = await strings.get_find_user_desc(user_info.id, user_info.nickname, user_info.lvl,
                                                        user_info.glory,
                                                        user_info.course, await user_info.get_glory_rank())

            else:
                text = strings.mob_desc_main_word[4]
                clan_info = Clan(*await DB.get_clan_info_with_clan_id(arg))
                text += f"{await clan_info.get_clan_emoji} {clan_info.name}\n\n" \
                        f"{await clan_info.get_clan_leader_text}" \
                        f"{await clan_info.get_clan_users_count()}" \
                        f"{await clan_info.get_clan_power}"

                user_info = await get_user_info(message.from_user.id)
                if user_info.clan is None:
                    reply_markup = await inline.get_one_item_keyb(strings.send_req_to_clan, f"send_req_{clan_info.id}")


            await bot.send_message(message.from_user.id, text, reply_markup=reply_markup)

    except TypeError:
        pass


async def have_acces(user_id):
    try:
        user_clan = await get_clan_info(user_id)
        if user_clan is not None:
            user_clan_info = await DB.get_clan_user(user_id)
            if user_clan_info[2] == 1 or user_clan_info[2] == 2:
                return True

    except TypeError:
        return False

