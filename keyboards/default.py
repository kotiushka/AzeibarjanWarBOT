from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_trick, get_fight_room, get_fight_room_u


async def buttons_start_choose_course():
    b1 = KeyboardButton(strings.start_choose_course[0])
    b2 = KeyboardButton(strings.start_choose_course[1])
    b3 = KeyboardButton(strings.start_choose_course[2])
    b_start = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    b_start.row(b1, b2, b3)
    return b_start


# кнопка которая на старте помогает выбрать ник предлагая юзернейм.
async def button_start_send_nickname(message: types.Message):
    b1 = KeyboardButton(message.from_user.username)
    b_start = ReplyKeyboardMarkup(resize_keyboard=True)
    b_start.add(b1)
    return b_start


async def buttons_menu(user_id, city=True, coliseum=False):
    b1 = KeyboardButton(strings.menuMainButtonsList[0])
    if city:
        b2 = KeyboardButton(strings.menuMainButtonsList[1])
    elif not city and not coliseum:
        b2 = KeyboardButton(strings.menuMainButtonsList[8])
    else:
        b2 = KeyboardButton(strings.fight_users_buttons[0])


    b3 = KeyboardButton(strings.menuMainButtonsList[2])
    b4 = KeyboardButton(strings.menuMainButtonsList[3])
    b5 = KeyboardButton(strings.menuMainButtonsList[4])
    b6 = KeyboardButton(strings.menuMainButtonsList[5])
    b7 = KeyboardButton(strings.menuMainButtonsList[6])
    b8 = KeyboardButton(strings.menuMainButtonsList[7])
    b_start = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    b_start.add(b1, b2).add(b3, b4).add(b5, b6).add(b7, b8)
    return b_start.add(strings.admin_button) if user_id in config.ADMIN_ID else b_start


async def hero_menu():
    b1 = KeyboardButton(strings.hero_buttots_keyb[0])
    b2 = KeyboardButton(strings.hero_buttots_keyb[1])
    b3 = KeyboardButton(strings.hero_buttots_keyb[2])
    b4 = KeyboardButton(strings.hero_buttots_keyb[3])
    b5 = KeyboardButton(strings.hero_buttots_keyb[4])
    b6 = KeyboardButton(strings.hero_buttots_keyb[5])
    b7 = KeyboardButton(strings.hero_buttots_keyb[6])
    b_start = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    b_start.add(b1, b2).add(b3, b4).add(b5, b6).add(b7)
    return b_start


async def npc_menu(city: str):
    cities = {"baki": strings.nps_baki_list[:-1], "karabah": strings.npc_karabah_list, "gandja": strings.npc_gandja_list}
    nlist = cities[city]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for button in nlist:
        keyboard.insert(button)
    return keyboard.add(strings.nps_baki_list[-1])

async def hero_tricks_menu():
    b_tricks = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    active_tricks = KeyboardButton(strings.trainer_button_list[1])
    know_tricks = KeyboardButton(strings.trainer_button_list[2])
    change_tricks = [KeyboardButton(strings.trainer_button_list[3] + str(i)) for i in range(1, 4)]
    back = strings.trainer_button_list[4]
    return b_tricks.add(active_tricks, know_tricks).add(*change_tricks).add(back)




async def cancel_button():
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        strings.cancel_transition)



async def fight_act(attack: bool, user_info: User, is_empty=False, is_online=False):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    async def get_buttons(keyb, start, end):
        for action in strings.fight_actions_buttons[start:end]:
            keyb.insert(action)
        return keyb

    async def get_trick_array(user_id, online):
        resultat = []
        for i in tricks:
            if i is not None:
                trick = await get_trick(i)
                fight_info = await get_fight_room(user_id) if not online else await get_fight_room_u(user_id)
                need_items = await trick.get_need_round_items
                if (trick.repeat != 0 and trick.id not in await fight_info.get_used_tricks(user_id)) or trick.repeat == 0:
                    attack_and_block = await fight_info.attack_and_block(user_id)
                    if attack_and_block[0] >= need_items[0] and attack_and_block[1] >= need_items[1]:
                        resultat.append(trick.title)
        return resultat

    if attack is False:
        keyboard = await get_buttons(keyboard, 5, 10)

    else:
        tricks = user_info.get_tricks
        if not is_empty and (tricks[0] or tricks[1] or tricks[1]):
            array = await get_trick_array(user_info.id, is_online)

            if array:
                keyboard = await get_keyboard_nested(array, to_loc=False)
                keyboard.add(strings.skip)
            else:
                keyboard = await get_buttons(keyboard, 0, 5)

        else:
            keyboard = await get_buttons(keyboard, 0, 5)

    return keyboard.add(strings.fight_actions_buttons[-1]) if not is_online else keyboard.add(strings.surrender)


async def get_fight_res_button(text):
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(text)


async def get_keyboard_nested(buttons: list, row_width=2, to_loc=True):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
    for i in buttons:
        keyboard.insert(i)
    return keyboard.add(strings.to_location) if to_loc else keyboard


async def yes_or_no_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(strings.yes_or_no[0], strings.yes_or_no[1])
    return keyboard




async def top_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for i in strings.top_titles[:-1]:
        keyboard.insert(i)
    return keyboard.add(strings.top_titles[-1])


async def point_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for i in strings.point_buttons:
        keyboard.insert(i)
    return keyboard


async def menu_chield_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for i in strings.menu_chield_buttons_text:
        keyboard.insert(i)
    return keyboard

async def settings_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    arr = strings.settings_buttons_text
    keyboard.add(arr[0])
    keyboard.add(arr[1], arr[2])
    keyboard.add(arr[3])
    return keyboard

async def help_message_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for i in strings.help_message_buttons:
        keyboard.insert(i)
    return keyboard


async def clan_default_buttons(have_invites):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for button_text in strings.clan_default_buttons[:-2]:
        keyboard.insert(button_text)
    keyboard.add(strings.my_votes)

    if have_invites:
        keyboard.insert(strings.clan_default_buttons[-2])

    return keyboard.add(strings.clan_default_buttons[-1])


async def clan_buttons(is_head=False):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for button_text in strings.clan_buttons[:-2]:
        keyboard.insert(button_text)
    if is_head == 2:
        keyboard.insert(strings.clan_buttons[-1])
        keyboard.insert(strings.control_clan_invites_buttons[0])

    elif is_head == 1:
        keyboard.insert(strings.control_clan_invites_buttons[0])

    keyboard.insert(strings.clan_buttons[2])

    return keyboard.add(strings.hero_buttots_keyb[6])


async def clan_controll():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.insert(strings.control_clan_invites_buttons[1])
    keyboard.insert(strings.control_clan_invites_buttons[2])
    return keyboard.add(strings.control_clan_invites_buttons[3])


async def coupon_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for button in strings.coupons_buttons:
        keyboard.insert(button)
    return keyboard


async def admin_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for button in strings.admin_buttons:
        keyboard.add(button)
    return keyboard


async def change_event_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for button in strings.change_event_buttons:
        keyboard.insert(button)
    return keyboard


