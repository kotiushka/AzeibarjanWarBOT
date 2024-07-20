from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.deep_linking import get_start_link

from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_trick, get_user_info, get_item, get_resource, get_quest


async def start_game():
    button = InlineKeyboardButton(text=strings.start_game_inlineButton, callback_data="start_game")
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(button)

    return keyboard


async def start_compliteReg():
    button = InlineKeyboardButton(text=strings.startCompliteRegInline, callback_data="start_game_complite")
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(button)

    return keyboard


async def dealer_buttons(callback):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    k1 = InlineKeyboardButton(text=strings.dealer_button_list[0], callback_data=f"weapon_{callback}")
    k2 = InlineKeyboardButton(text=strings.dealer_button_list[1], callback_data=f"protect_{callback}")
    k3 = InlineKeyboardButton(text=strings.dealer_button_list[2], callback_data=f"products_{callback}")
    k4 = InlineKeyboardButton(text=strings.dealer_button_list[3], callback_data=f"resources_{callback}")
    keyboard.add(k1, k2)
    keyboard.add(k3, k4)
    return keyboard


async def trainer_buttons(callback):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    k1 = InlineKeyboardButton(text=strings.trainer_button_list[0], callback_data=f"trick_{callback}")
    return keyboard.add(k1)


async def dealer_buttons_weapon(callback):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    k1 = InlineKeyboardButton(text=strings.dealer_weapon_button_list[0], callback_data=f"sword_{callback}")
    k2 = InlineKeyboardButton(text=strings.dealer_weapon_button_list[2], callback_data=f"dagger_{callback}")
    k3 = InlineKeyboardButton(text=strings.dealer_weapon_button_list[1], callback_data=f"axe_{callback}")
    k5 = InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"back_{callback}")
    keyboard.add(k1, k3, k2).add(k5)

    return keyboard


async def dealer_buttons_protect(callback):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=4)
    k1 = InlineKeyboardButton(text=strings.dealer_protect_button_list[0], callback_data=f"helmet_{callback}")
    k2 = InlineKeyboardButton(text=strings.dealer_protect_button_list[1], callback_data=f"armor_{callback}")
    k3 = InlineKeyboardButton(text=strings.dealer_protect_button_list[2], callback_data=f"shield_{callback}")
    k4 = InlineKeyboardButton(text=strings.dealer_protect_button_list[3], callback_data=f"gloves_{callback}")
    k5 = InlineKeyboardButton(text=strings.dealer_protect_button_list[4], callback_data=f"boots_{callback}")
    k6 = InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"back_{callback}")
    keyboard.add(k1, k2).add(k3, k4).add(k5).add(k6)

    return keyboard


async def dealer_buttons_products(callback):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    k1 = InlineKeyboardButton(text=strings.dealer_product_button_list[0], callback_data=f"necklace_{callback}")
    k2 = InlineKeyboardButton(text=strings.dealer_product_button_list[1], callback_data=f"ring_{callback}")
    k3 = InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"back_{callback}")
    keyboard.add(k1, k2).add(k3)

    return keyboard


async def dynamic_item_sale(item_names, cb: CallbackData, button_return, user_id, type, sale=0, is_coupon=False):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)

    button_list = []

    user_info = await get_user_info(user_id)
    s = "💰" if not is_coupon else "🎫"
    for item in item_names:
        if type == "item":
            current_item = await get_item(item)
            button_text = f"{current_item.title} - {int(current_item.cost - ((current_item.cost * sale) / 100))}{s}{'🔻' if user_info.lvl < current_item.need_lvl else ''}"

        elif type == "trick":
            current_item = await get_trick(item)
            button_text = f"{current_item.title} - {int(current_item.cost - ((current_item.cost * sale) / 100))}{s}{'🔻' if user_info.lvl < current_item.need_lvl else ''}"

        else:
            current_item = await get_resource(item)
            button_text = f"{current_item.title} - {int(current_item.cost - ((current_item.cost * sale) / 100))}{s}"

        if type == "trick":
            item_use = await DB.check_item_on_inventory(current_item.id, user_info.nickname)
            button_text += " ✅" if item_use else ""

        button_list.append(InlineKeyboardButton(text=button_text, callback_data=cb.new(item)))

    keyboard.add(*button_list)
    return keyboard.add(InlineKeyboardButton(text=strings.hero_buttots_keyb[-1],
                                             callback_data=button_return)) if button_return is not None else keyboard


async def buy_item(callback_back, cb: CallbackData, item_name, action=0, symbol="💰"):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    # Купить
    k1 = InlineKeyboardButton(text=strings.buy_item_title[action].format(symbol), callback_data=cb.new(item_name))
    # Назад
    k2 = InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"{callback_back}")

    keyboard.add(k1).add(k2)
    return keyboard


async def dealer_buy_item_only_back(callback_back):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    k1 = InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"{callback_back}")
    keyboard.add(k1)
    return keyboard


async def get_items_on_inventory(nickname, item_selected: CallbackData):
    all_items = await DB.get_all_items_from_inventory(nickname)
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    types = ["sword", "axe", "dagger", "helmet", "armor", "gloves", "boots", "shield", "ring", "necklace", "accessory"]
    aviables = set()
    for item in all_items:
        item_type = item[0]
        if item_type in types and item_type not in aviables:
            keyboard.insert(await return_keyboard_type(item_type, nickname, item_selected))
            aviables.add(item_type)
    return keyboard


async def return_keyboard_type(type_keyb, nickname, item_selected: CallbackData):
    return InlineKeyboardButton(
        text=f"{dicts.item_buttons[type_keyb]} ({str(await DB.get_item_count(nickname, type_keyb))})",
        callback_data=item_selected.new(type_keyb))


async def list_keyboard(item_list: list, first_num, last_num, cb_1: CallbackData, cb_2: CallbackData,
                        cb_3: CallbackData, is_trade=False, back_button="back_hero"):
    global i
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)

    list_len = len(item_list)

    for i in item_list[first_num:last_num]:
        try:
            item = await get_item(i[0])
        except TypeError:
            item = await get_resource(i[0])

        item_use = await DB.get_item_use(i[1])
        item_title = item.title
        symbol = ""

        if item_use[1] != 0:
            symbol += f" +{item_use[1]}"

        if is_trade:
            if not item_use[0] == "yes":
                keyboard.add(InlineKeyboardButton(text=item_title + symbol, callback_data=cb_3.new(
                    str(item.id) + f"-{i[1]}-{item.type}-{first_num}-{last_num}")))
        else:
            symbol += " ✅" if item_use[0] == "yes" else ""
            keyboard.add(InlineKeyboardButton(text=item_title + symbol, callback_data=cb_3.new(
                str(item.id) + f"-{i[1]}-{item.type}-{first_num}-{last_num}")))

    if list_len > 5:
        try:
            item = await get_item(i[0])
        except TypeError:
            item = await get_resource(i[0])

        k2 = InlineKeyboardButton(text="➡", callback_data=cb_1.new(
            f"{str(first_num)}-{str(last_num)}-{item.type}"))
        k1 = InlineKeyboardButton(text="⬅", callback_data=cb_2.new(
            f"{str(first_num)}-{str(last_num)}-{item.type}"))
        keyboard.add(k1, k2)

    keyboard.add(InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=back_button))

    return keyboard


async def text_buttons_keyboard_trick(item_list: list, first_num, last_num, action: CallbackData, trick_number=0):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)

    k2 = InlineKeyboardButton(text="➡",
                              callback_data=action.new(f"{str(first_num)}-{str(last_num)}-{trick_number}-next"))

    k1 = InlineKeyboardButton(text="⬅",
                              callback_data=action.new(f"{str(first_num)}-{str(last_num)}-{trick_number}-prev"))
    keyboard.add(k1, k2)

    text = item_list[first_num:last_num]
    text = "\n".join(text)

    return [keyboard, text]


async def text_buttons_keyboard_resources(res_type, item_list: list, first_num, last_num, action: CallbackData):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)

    k1 = InlineKeyboardButton(text="⬅",
                              callback_data=action.new(f"{str(first_num)}-{str(last_num)}-{res_type}-prev"))

    k2 = InlineKeyboardButton(text="➡",
                              callback_data=action.new(f"{str(first_num)}-{str(last_num)}-{res_type}-next"))

    k3 = InlineKeyboardButton(text=strings.to_res, callback_data="to_res")
    keyboard.add(k1, k2).add(k3)

    need_items = item_list[first_num:last_num]

    return [keyboard, need_items]


# Клавиатура при нажатии на предмет - заточить, надеть/снять
async def item_selected_keyboard(item_id, item, item_type, first_num, last_num, cb: CallbackData):
    item_use = await DB.get_item_use(item_id)
    item_use = item_use[0]

    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)

    if item_use == "yes":
        # Снять
        keyboard.add(
            InlineKeyboardButton(text=strings.item_actions_inventory[1],
                                 callback_data=cb.new(f"{item_id}-{item}-{item_type}-off")))
    else:
        # Надеть
        keyboard.add(
            InlineKeyboardButton(text=strings.item_actions_inventory[0],
                                 callback_data=cb.new(f"{item_id}-{item}-{item_type}-on")))
    # Заточтить
    keyboard.add(
        InlineKeyboardButton(text=strings.item_actions_inventory[2],
                             callback_data=cb.new(f"{item_id}-{item}-{item_type}-up")))
    # Назад
    keyboard.add(InlineKeyboardButton(text=strings.item_actions_inventory[3], callback_data=cb.new(
        f"{item_id}-{item}-{item_type}-{first_num}-{last_num}-back")))

    return keyboard


# Клавиатура заточить/нет
async def upper_keyboard(cb: CallbackData, current_item):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(InlineKeyboardButton(text=strings.item_actions_inventory[2], callback_data=cb.new(
        f"{current_item[0]}-{current_item[2]}-{current_item[3]}-{current_item[4]}-{current_item[5]}")))
    keyboard.add(InlineKeyboardButton(text=strings.item_actions_inventory[4], callback_data=cb.new("no")))
    return keyboard


async def distribute_points(cb: CallbackData, lvl: int):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)

    keyboard.insert(InlineKeyboardButton(text=strings.distribute_points_inline_text[0], callback_data=cb.new("power")))
    keyboard.insert(InlineKeyboardButton(text=strings.distribute_points_inline_text[1], callback_data=cb.new("force")))
    if lvl >= 10:
        keyboard.insert(
            InlineKeyboardButton(text=strings.distribute_points_inline_text[2], callback_data=cb.new("dexterity")))
        keyboard.insert(
            InlineKeyboardButton(text=strings.distribute_points_inline_text[3], callback_data=cb.new("intuition")))
    return keyboard


async def get_one_item_keyb(text, callback):
    """
    Функция для того чтобы получить 1 inline button
    :param text: текст кнопки
    :param callback: калбек кнопки
    :return: клавиатуру с указанным тестом и калбеком
    """
    return InlineKeyboardMarkup(resize_keyboard=True, row_width=1) \
        .add(InlineKeyboardButton(text=text, callback_data=callback))


async def item_no_have_actions():
    actions = [InlineKeyboardButton(text=strings.no_have_item_actions[0], callback_data="back_to_shop_c"),
               InlineKeyboardButton(text=strings.no_have_item_actions[1], url=f"t.me/{strings.shop_chat}")]
    return InlineKeyboardMarkup(resize_keyboard=True, row_width=2).add(*actions)


async def resources_keyboard(nickname, in_trade=False):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)

    for item in strings.item_types_res:
        item_type_count = await DB.get_item_count(nickname, item)
        if item_type_count != 0:
            callback_data = item + "_trade" if in_trade else item
            keyboard.add(InlineKeyboardButton(text=strings.item_types_str[item] + f" [{item_type_count}]",
                                              callback_data=callback_data))

    if in_trade:
        keyboard.add(InlineKeyboardButton(text=strings.hero_buttots_keyb[6], callback_data="back_to_offer"))

    return keyboard


async def data_info_help():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for item_info in range(0, 4):
        keyboard.add(InlineKeyboardButton(text=strings.data_help_buttons_text[item_info],
                                          switch_inline_query_current_chat=strings.data_help_answers_text[item_info]))
    return keyboard


async def find_user():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    return keyboard.add(InlineKeyboardButton(text=strings.find_user,
                                             switch_inline_query_current_chat=strings.data_help_answers_text[4]))


async def send_trade(user_id):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    return keyboard.add(InlineKeyboardButton(text=strings.offer_trade, callback_data=f"offer-{user_id}"))


async def accept_or_no_trade(user_to_trade):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text=strings.offer_accept_or_no[0], callback_data=f"accept-{user_to_trade}"))
    keyboard.add(InlineKeyboardButton(text=strings.offer_accept_or_no[1], callback_data=f"decline-{user_to_trade}"))
    return keyboard


async def trade_buttons():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text=strings.buttons_trade[0], callback_data=strings.buttons_trade_callbaks[0]))
    keyboard.add(InlineKeyboardButton(text=strings.buttons_trade[1], callback_data=strings.buttons_trade_callbaks[1]))
    keyboard.add(InlineKeyboardButton(text=strings.buttons_trade[2], callback_data=strings.buttons_trade_callbaks[2]))
    keyboard.add(InlineKeyboardButton(text=strings.buttons_trade[3], callback_data=strings.buttons_trade_callbaks[3]))
    keyboard.add(InlineKeyboardButton(text=strings.buttons_trade[4], callback_data=strings.buttons_trade_callbaks[4]))
    return keyboard


async def gold_coupon_trade_buttons(item_type: str):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    res_info = await strings.get_coupons_or_gold_buttons(item_type)

    for button in res_info:
        keyboard.insert(InlineKeyboardButton(text=button, callback_data=res_info[button]))
    return keyboard.add(InlineKeyboardButton(text=strings.hero_buttots_keyb[6], callback_data="back_to_offer"))


async def offer_result_buttons(trade_id: int):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(InlineKeyboardButton(text=strings.offer_resultat_buttons[0], callback_data=f"agree_offer-{trade_id}"))
    keyboard.add(InlineKeyboardButton(text=strings.offer_resultat_buttons[1], callback_data=f"change_offer-{trade_id}"))
    return keyboard


async def select_emoji_clan(emojis, current_emoji=999, aviable_emojies=[]):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    for emoji in emojis:
        if emoji[0] == current_emoji:
            text = f"{emoji[1]} ✅"
        elif emoji[0] not in aviable_emojies:
            text = f"{emoji[1]} {emoji[2]} 💰"
        else:
            text = f"{emoji[1]} 0 💰"
        keyboard.insert(InlineKeyboardButton(text=text, callback_data=f"emoji-{emoji[0]}-{emoji[2]}"))

    return keyboard


async def check_clan_users(clan_id):
    return InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text=strings.check_clan_users_button[0],
                                                                               switch_inline_query_current_chat=
                                                                               f"{strings.check_clan_users_button[1]}{clan_id}"))


async def get_clan_user_buttons(user_id: int, user_status, is_admin: bool):
    if is_admin:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        if user_status == 0:
            keyboard.add(
                InlineKeyboardButton(text=strings.clan_user_actions[0], callback_data=f"set_pre_head-{user_id}"))
        else:
            keyboard.add(
                InlineKeyboardButton(text=strings.clan_user_actions[1], callback_data=f"unset_pre_head-{user_id}"))
        keyboard.add(InlineKeyboardButton(text=strings.clan_user_actions[2], callback_data=f"give_head-{user_id}"))
        keyboard.add(InlineKeyboardButton(text=strings.clan_user_actions[3], callback_data=f"cick-{user_id}"))
        return keyboard

    else:
        return None


async def find_clan_keyb():
    return InlineKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text=strings.search_clan[0],
                                                                               switch_inline_query_current_chat=
                                                                               f"{strings.search_clan[1]}"))


async def accept_decline_invite(clan_id):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(InlineKeyboardButton(text=strings.offer_accept_or_no[0], callback_data=f"clan_inv-accept-{clan_id}"))
    keyboard.add(InlineKeyboardButton(text=strings.offer_accept_or_no[1], callback_data=f"clan_inv-decline-{clan_id}"))
    return keyboard


async def accept_decline_clan_req(user_id):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(InlineKeyboardButton(text=strings.clan_accept_or_no[0], callback_data=f"clan_req-accept-{user_id}"))
    keyboard.add(InlineKeyboardButton(text=strings.clan_accept_or_no[1], callback_data=f"clan_req-decline-{user_id}"))
    return keyboard


async def clan_settings(clan_id):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    for button in strings.clan_settings_buttons:
        keyboard.insert(
            InlineKeyboardButton(text=button, callback_data=strings.clan_settings_buttons[button].format(clan_id)))

    return keyboard


async def change_clan_title():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.insert(InlineKeyboardButton(text=strings.yes_or_no[0], callback_data="change_clan_title-yes"))
    keyboard.insert(InlineKeyboardButton(text=strings.yes_or_no[1], callback_data="change_clan_title-no"))
    return keyboard


async def delete_clan():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.insert(InlineKeyboardButton(text=strings.yes_or_no[0], callback_data="delete_clan-yes"))
    keyboard.insert(InlineKeyboardButton(text=strings.yes_or_no[1], callback_data="change_clan_title-no"))
    return keyboard


async def add_coupons_message():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    for cost in config.COUPONS_COST:
        keyboard.add(InlineKeyboardButton(text=strings.coupon_buy_message.format(cost, config.COUPONS_COST[cost]),
                                          url=config.ADMIN_LINK))
    return keyboard


async def shop_coupons_message():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    for button in strings.coupons_shop:
        keyboard.insert(InlineKeyboardButton(text=button, callback_data=strings.coupons_shop[button]))
    return keyboard


async def quest_buttons(user_id):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    today_quests = await DB.select_today_quests(user_id)
    if not today_quests:
        user_info = await get_user_info(user_id)
        await DB.add_today_quests(user_id, user_info.lvl)

    today_quests = await DB.select_today_quests(user_id)
    for quest in today_quests:
        quest = await get_quest(quest[0])
        received = await DB.get_quest_user_received(user_id, quest.id)

        symbol = ""
        if received == quest.required:
            symbol = "✅"
        elif received != quest.required and received is not None:
            symbol = "✔️"

        keyboard.add(InlineKeyboardButton(text=f"{quest.title} {symbol}", callback_data=f"quest-{quest.id}"))

    return keyboard


async def quest_tap_buttons(user_id, quest_id):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    received = await DB.get_quest_user_received(user_id, quest_id)
    if received is not None:
        if not await DB.get_succes_quest(user_id, quest_id):
            current_quest = await get_quest(quest_id)
            if await DB.get_quest_user_received(user_id, quest_id) == current_quest.required:
                keyboard.add(InlineKeyboardButton(text=strings.take_reward, callback_data=f"quest-reward-{quest_id}"))
            keyboard.add(InlineKeyboardButton(text=strings.cancel_quest, callback_data=f"quest-decline-{quest_id}"))

    else:
        keyboard.add(InlineKeyboardButton(text=strings.take_quest, callback_data=f"quest-accept-{quest_id}"))

    keyboard.add(InlineKeyboardButton(text=strings.hero_buttots_keyb[6], callback_data=f"back_to_quests"))
    return keyboard


async def send_ref_message(user_id):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    return keyboard.add(InlineKeyboardButton(text=strings.invite_to_game, url=
    f"https://t.me/share/url?url={strings.invite_game_message.format(await get_start_link(user_id))}"))


async def get_event_reward(event_reward):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    if not event_reward:
        return keyboard.add(InlineKeyboardButton(text=strings.event_buttons[0], callback_data=f"get_event_reward"))
    return keyboard.add(
        InlineKeyboardButton(text=strings.event_buttons[1], callback_data=f"event_reward_already_taked"))


async def alchimic_buttons(alc):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    return keyboard.add(
        InlineKeyboardButton(text=list(strings.item_types_str.values())[-1], callback_data=f"{alc}_potions"))


async def boxes_shaman():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    for box in strings.boxes_rarity_list:
        keyboard.insert(InlineKeyboardButton(strings.boxes_rarity_list[box], callback_data=box))
    return keyboard


async def boxe_actions(box_type):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.insert(InlineKeyboardButton(strings.box_open, callback_data=f"open_box-{box_type}"))
    return keyboard.insert(InlineKeyboardButton(strings.hero_buttots_keyb[6], callback_data="boxes_back"))


async def box_back():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    return keyboard.insert(InlineKeyboardButton(strings.hero_buttots_keyb[6], callback_data="boxes_back"))


# blackstih buttons
async def blacksmith_buttons(callback):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    k1 = InlineKeyboardButton(text=strings.dealer_button_list[0], callback_data=f"{callback}_weapon")
    k2 = InlineKeyboardButton(text=strings.dealer_button_list[1], callback_data=f"{callback}_protect")
    k3 = InlineKeyboardButton(text=strings.dealer_button_list[2], callback_data=f"{callback}_products")
    keyboard.add(k1, k2)
    keyboard.add(k3)
    return keyboard


async def blacksmith_buttons_weapon(callback):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    k1 = InlineKeyboardButton(text=strings.dealer_weapon_button_list[0], callback_data=f"{callback}_sword")
    k2 = InlineKeyboardButton(text=strings.dealer_weapon_button_list[2], callback_data=f"{callback}_dagger")
    k3 = InlineKeyboardButton(text=strings.dealer_weapon_button_list[1], callback_data=f"{callback}_axe")
    k5 = InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"{callback}_main_back")
    keyboard.add(k1, k3, k2).add(k5)

    return keyboard


async def blacksmith_protect(callback):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=4)
    k1 = InlineKeyboardButton(text=strings.dealer_protect_button_list[0], callback_data=f"{callback}_helmet")
    k2 = InlineKeyboardButton(text=strings.dealer_protect_button_list[1], callback_data=f"{callback}_armor")
    k3 = InlineKeyboardButton(text=strings.dealer_protect_button_list[2], callback_data=f"{callback}_shield")
    k4 = InlineKeyboardButton(text=strings.dealer_protect_button_list[3], callback_data=f"{callback}_gloves")
    k5 = InlineKeyboardButton(text=strings.dealer_protect_button_list[4], callback_data=f"{callback}_boots")
    k6 = InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"{callback}_main_back")
    keyboard.add(k1, k2).add(k3, k4).add(k5).add(k6)

    return keyboard


async def blacksmith_buttons_products(callback):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    k1 = InlineKeyboardButton(text=strings.dealer_product_button_list[0], callback_data=f"{callback}_necklace")
    k2 = InlineKeyboardButton(text=strings.dealer_product_button_list[1], callback_data=f"{callback}_ring")
    k3 = InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"{callback}_main_back")
    keyboard.add(k1, k2).add(k3)

    return keyboard


async def blacksmith_items(bs, item_type, city):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    cur_items = await DB.get_blacksmith_items_to_craft(city, item_type)
    for item in cur_items:
        current_item = await get_item(item[-1])
        keyboard.add(InlineKeyboardButton(text=current_item.title, callback_data=f"bcraft-{current_item.id}-{bs}"))

    if item_type in ["sword", "axe", "dagger"]:
        keyboard.add(InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"{bs}_weapon"))
    elif item_type in ["necklace", "ring"]:
        keyboard.add(InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"{bs}_products"))
    else:
        keyboard.add(InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"{bs}_protect"))


    return keyboard


async def blacksmith_craft_back(bs, item_id, item_type):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)

    keyboard.add(InlineKeyboardButton(text=strings.to_craft, callback_data=f"create-{item_id}-{bs}"))

    keyboard.add(InlineKeyboardButton(text=strings.hero_buttots_keyb[-1], callback_data=f"{bs}_{item_type}"))

    return keyboard


