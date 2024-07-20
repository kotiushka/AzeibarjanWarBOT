from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT import config
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate, IsClanHead, IsClanHeadOrAdmin, UserInClan, UserNotInClan
from AzeibarjanWarBOT.keyboards import default, inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src.clan import Clan
from AzeibarjanWarBOT.state.states import CreateClan, ClanSettings
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info, get_clan_info, get_resource
from AzeibarjanWarBOT.utils.functions import ret_city, buy_item

cb_item_tap = CallbackData("potion", "tap")
cb_buy_item = CallbackData("buy", "res")


@dp.message_handler(IsPrivate(), text=[strings.menuMainButtonsList[3], strings.control_clan_invites_buttons[3]])
async def clan_message(message: types.Message):
    """Кнопка Клан в основном меню"""
    if not bool(await DB.get_user_clan(message.from_user.id)):
        user_info = await get_user_info(message.from_user.id)
        await bot.send_message(message.from_user.id, strings.none_clan_message,
                               reply_markup=await default.clan_default_buttons(user_info.clan_invite_join))

    else:
        user_clan = await get_clan_info(message.from_user.id)
        user_clan_info = await DB.get_clan_user(message.from_user.id)
        await bot.send_message(message.from_user.id, await user_clan.get_clan_description,
                               reply_markup=await default.clan_buttons(user_clan_info[2]))


@dp.message_handler(IsPrivate(), UserNotInClan(), text=strings.clan_default_buttons[1])
async def create_clan_message(message: types.Message):
    """keyboard кнопка Создать клан"""
    await bot.send_message(message.from_user.id, strings.clan_create_message,
                           reply_markup=await inline.get_one_item_keyb(message.text, "create_clan"))


@dp.callback_query_handler(UserNotInClan(), text="create_clan")
async def create_clan(call: types.CallbackQuery):
    """inline кнопка Создать клан"""
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, reply_markup=None,
                                        message_id=call.message.message_id)

    user_info = await get_user_info(call.from_user.id)
    if user_info.gold >= config.CLAN_COST:
        await DB.update_balance(config.CLAN_COST, "-", call.from_user.id)
        await CreateClan.create.set()
        await bot.send_message(call.from_user.id, strings.clan_creation_requirements,
                               reply_markup=await default.get_fight_res_button(strings.cancel_del))

    else:
        await bot.send_message(call.from_user.id, strings.get_you_cant_buy_it.format(user_info.gold))


@dp.message_handler(IsPrivate(), text=strings.cancel_del, state=[CreateClan.create, CreateClan.choice_emoji])
async def cancel_creating_clan(message: types.Message, state: FSMContext):
    """Отмена создания клана"""
    await state.finish()
    await DB.update_balance(config.CLAN_COST, "+", message.from_user.id)
    await DB.cancel_clan_creating(message.from_user.id)
    await bot.send_message(message.from_user.id, strings.creating_clan_is_canceled)
    await ret_city(message.from_user.id)


@dp.message_handler(IsPrivate(), state=[CreateClan.create, ClanSettings.title])
async def type_name_clan(message: types.Message, state: FSMContext):
    """Ввод названия клана"""
    if message.text.isalpha() and len(message.text) <= 20:
        if not await DB.get_clan_busy_name(message.text):

            if await state.get_state() == "CreateClan:create":
                await DB.create_clan(message.text)
                await DB.add_user_to_clan(message.text, message.from_user.id, True)
                await CreateClan.choice_emoji.set()
                await bot.send_message(message.from_user.id, strings.clan_choice_emoji,
                                       reply_markup=await inline.select_emoji_clan(await DB.select_clan_emojies()))

            else:
                user_clan = await get_clan_info(message.from_user.id)
                await DB.update_clan_title(user_clan.id, message.text)
                await bot.send_message(message.from_user.id, strings.successfully_changed_clan_title.format(message.text))
                await state.finish()
                await ret_city(message.from_user.id)

        else:
            await bot.send_message(message.from_user.id, strings.clan_name_is_busy)
    else:
        await bot.send_message(message.from_user.id, strings.clan_name_is_unaviable)


@dp.callback_query_handler(text_startswith="emoji-", state=[None, CreateClan.choice_emoji])
async def choice_emoji(call: types.CallbackQuery, state: FSMContext):
    """Выбор конкретного эмодзи из предложеных"""
    emoji_id, emoji_cost = map(int, call.data.split("-")[1:])
    user_clan_id = await DB.get_user_clan_id(call.from_user.id)

    user_info = await get_user_info(call.from_user.id)

    clan_info = await get_clan_info(call.from_user.id)

    if emoji_cost > user_info.gold and emoji_id not in await clan_info.get_aviable_emojies:
        return await call.answer(strings.get_you_cant_buy_it.format(user_info.gold))

    if await state.get_state() is not None:
        await emoji_last_choice(state, call, emoji_cost, user_clan_id, emoji_id)

    else:
        if await IsClanHead().check(call):
            await DB.set_clan_emoji(user_clan_id, emoji_id)

            if emoji_id not in await clan_info.get_aviable_emojies and emoji_cost != 0:
                await DB.add_aviable_emojies(user_clan_id, emoji_id)
                await DB.update_balance(emoji_cost, "-", call.from_user.id)
                clan_info = await get_clan_info(call.from_user.id)
                await call.answer(strings.emoji_was_buy.format(await clan_info.get_clan_emoji, emoji_cost))

            clan_info = await get_clan_info(call.from_user.id)
            await bot.edit_message_reply_markup(chat_id=call.from_user.id,
                                                message_id=call.message.message_id,
                                                reply_markup=await inline.select_emoji_clan(
                                                    await DB.select_clan_emojies(),
                                                    clan_info.current_emoji,
                                                    await clan_info.get_aviable_emojies
                                                ))

            await call.answer(strings.emoji_choised.format(await clan_info.get_clan_emoji))


        else:
            await bot.send_message(call.from_user.id, strings.not_have_acces_head)


@dp.callback_query_handler(UserInClan(), IsClanHead(), text=["delete-clan", "delete_clan-yes"])
async def delete_clan_first(call: types.CallbackQuery):
    """Удалить клан"""
    if call.data != "delete-clan":
        user_info = await get_user_info(call.from_user.id)
        await DB.delete_clan(user_info.clan)
        await bot.send_message(call.from_user.id, text=strings.clan_deleted)
        await ret_city(call.from_user.id)
    else:
        await bot.edit_message_text(chat_id=call.from_user.id, text=strings.are_you_sure_delete_clan, reply_markup=await inline.delete_clan(), message_id=call.message.message_id)


@dp.message_handler(IsPrivate(), state=CreateClan.choice_emoji)
async def choise_emoji_all_mess(message: types.Message):
    await bot.send_message(message.from_user.id, strings.cancel_clan_create,
                           reply_markup=await default.get_fight_res_button(strings.cancel_del))


async def emoji_last_choice(state: FSMContext, call: types.CallbackQuery, emoji_cost, user_clan_id, emoji_id):
    """Фунция для установки эмодзи"""
    if emoji_cost != 0:
        await DB.add_aviable_emojies(user_clan_id, emoji_id)
        await DB.update_balance(emoji_cost, "-", call.from_user.id)

    await state.finish()
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, reply_markup=None,
                                        message_id=call.message.message_id)

    await DB.set_clan_emoji(user_clan_id, emoji_id)
    await bot.send_message(call.from_user.id, strings.clan_successfully_created)
    await ret_city(call.from_user.id)


@dp.message_handler(UserInClan(), IsPrivate(), text=strings.clan_buttons[0])
async def user_list(message: types.Message):
    try:
        await bot.send_message(message.from_user.id,
                               strings.clan_users_casarm.format(await DB.get_clan_users_count(message.from_user.id)),
                               reply_markup=await inline.check_clan_users(
                                   await DB.get_user_clan_id(message.from_user.id)))
    except TypeError:
        return


@dp.message_handler(UserInClan(), IsPrivate(), commands='getclanuser')
async def get_clan_user(message: types.Message):
    try:
        get_user_id = int(message.text.split()[1])
        get_user_clan = await get_clan_info(get_user_id)
    except (ValueError, IndexError, TypeError):
        return

    g_user_info = await get_user_info(get_user_id)
    g_user_clan_info = await DB.get_clan_user(get_user_id)

    user_clan = await get_clan_info(message.from_user.id)
    user_clan_info = await DB.get_clan_user(message.from_user.id)

    if user_clan.id == get_user_clan.id:
        reply_markup = await inline.get_clan_user_buttons(get_user_id, g_user_clan_info[2], user_clan_info[
            2] == 2) if message.from_user.id != get_user_id else None
        text = f"{strings.user.format(await g_user_info.get_href_without_hp(), strings.get_user_status[g_user_clan_info[2]])}\n\n" \
               f"{strings.user_power.format(g_user_info.pvp_points)}"

        await bot.send_message(message.from_user.id, text, reply_markup=reply_markup)
    else:
        await bot.send_message(message.from_user.id, strings.user_not_in_your_clan)


@dp.callback_query_handler(UserInClan(), IsClanHead(),
                           text_startswith=["set_pre_head", "unset_pre_head", "cick", "give_head"])
async def set_unset_pre_head(call: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=None)
    try:
        user_clan_info = await DB.get_clan_user(call.from_user.id)
        user_set_unset = int(call.data.split("-")[1])
        user_to_cick_clan = await get_clan_info(user_set_unset)
        main_user_clan = await get_clan_info(call.from_user.id)

    except TypeError:
        return await call.answer(strings.something_went_wrong)

    if user_clan_info[2] == 2 and user_to_cick_clan.id == main_user_clan.id:
        call_type = call.data.split("-")[0]
        if call_type == "set_pre_head" or call_type == "unset_pre_head":
            pre_head = 1 if call_type == "set_pre_head" else 0
            await DB.set_unset_clan_pre_head(user_set_unset, pre_head)

            text_main_user = strings.successfully_set_pre_head if pre_head == 1 else strings.successfully_unset_pre_head
            text_changer_user = strings.you_was_set_pre_head if pre_head == 1 else strings.you_was_uset_pre_head

        elif call_type == "cick":
            await DB.cick_user(user_set_unset)
            text_main_user, text_changer_user = strings.user_successfully_was_cicked, strings.you_was_cicked

        else:
            await DB.set_unset_clan_pre_head(user_set_unset, 2)
            await DB.set_unset_clan_pre_head(call.from_user.id, 1)
            text_main_user, text_changer_user = strings.successfully_set_head, strings.successfully_unset_head

        await bot.send_message(call.from_user.id, text_main_user)
        await bot.send_message(user_set_unset, text_changer_user.format(main_user_clan.name))

    else:
        return await call.answer(strings.something_went_wrong)


@dp.message_handler(IsPrivate(), UserInClan(), text=strings.clan_buttons[2])
async def leave_clan(message: types.Message):
    """Выйти с клана"""
    user_clan_info = await DB.get_clan_user(message.from_user.id)
    if user_clan_info[2] == 2:
        await bot.send_message(message.from_user.id, strings.you_cant_leav)
    else:
        user_clan = await get_clan_info(message.from_user.id)
        await DB.cick_user(message.from_user.id)
        await bot.send_message(message.from_user.id, strings.you_was_leav.format(await user_clan.get_clan_title))
        await ret_city(message.from_user.id)


@dp.message_handler(IsPrivate(), UserInClan(), text=strings.clan_buttons[1])
async def clan_shop(message: types.Message):
    """Магазин клана"""
    await bot.send_message(message.from_user.id, strings.clan_shop_message,
                           reply_markup=await inline.dynamic_item_sale(["heal_1", "heal_2", "heal_3", "heal_4"],
                                                                       cb=cb_item_tap, button_return=None,
                                                                       user_id=message.from_user.id,
                                                                       type="resource", sale=10))


@dp.callback_query_handler(UserInClan(), text="potion_back_to_shop")
async def back_to_shop(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.from_user.id, text=strings.clan_shop_message,
                                message_id=call.message.message_id,
                                reply_markup=await inline.dynamic_item_sale(
                                    ["heal_1", "heal_2", "heal_3", "heal_4"],
                                    cb=cb_item_tap, button_return=None,
                                    user_id=call.from_user.id,
                                    type="resource", sale=10))


@dp.callback_query_handler(cb_item_tap.filter())
async def get_more_info_shop(call: types.CallbackQuery):
    """Нажатие на предмет в магазине клана"""
    if await UserInClan().check(call):
        resource_id = call.data.split(":")[1]
        current_item = await get_resource(resource_id)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=await current_item.get_item_description_full(10),
                                    reply_markup=await inline.buy_item("potion_back_to_shop", cb_buy_item,
                                                                       resource_id))


@dp.callback_query_handler(cb_buy_item.filter())
async def buy(call: types.CallbackQuery):
    if await UserInClan().check(call):
        await buy_item(call, "item", "back_to_shop", 10)


@dp.message_handler(IsPrivate(), UserNotInClan(), text=strings.clan_default_buttons[0])
async def search_clan(message: types.Message):
    """Поиск клана"""
    text = strings.list_aviable_clans + '\n\n'
    for clan in await DB.get_clans():
        clan = Clan(*clan)
        text += await clan.get_clan_text() + "\n\n"
    await bot.send_message(message.from_user.id, text, reply_markup=await inline.find_clan_keyb())


@dp.message_handler(IsPrivate(), UserNotInClan(), text=strings.my_votes)
async def my_votes(message: types.Message):
    """Мои приглашения"""
    user_info = await get_user_info(message.from_user.id)
    clan_invites = await user_info.get_clan_invites
    if clan_invites:
        await bot.send_message(message.from_user.id, strings.is_your_invites)
        for clan_invite in clan_invites:
            try:
                clan_info = Clan(*await DB.get_clan_info_with_clan_id(clan_invite))
            except TypeError:
                await DB.delete_clan_invite(message.from_user.id, clan_invites, clan_invite, False)
                continue
            await bot.send_message(message.from_user.id, await clan_info.get_clan_description,
                                   reply_markup=await inline.accept_decline_invite(clan_invite))

    else:
        await bot.send_message(message.from_user.id, strings.my_invites_empty_message)


@dp.message_handler(IsPrivate(), IsClanHeadOrAdmin(), text=strings.control_clan_invites_buttons[1])
async def want_joint(message: types.Message):
    """📊 Запросы на вступление"""
    clan_info = await get_clan_info(message.from_user.id)
    clan_requests = await DB.get_want_to_join_users(clan_info.id)
    if clan_requests:
        await bot.send_message(message.from_user.id, strings.is_your_requests)
        for user in await DB.get_want_to_join_users(clan_info.id):
            user_info = await get_user_info(user[0])
            await bot.send_message(message.from_user.id, await user_info.get_user_description,
                                   reply_markup=await inline.accept_decline_clan_req(user_info.id))
    else:
        await bot.send_message(message.from_user.id, strings.my_requests_empty_message)


@dp.message_handler(IsPrivate(), UserInClan(), IsClanHead(), text=strings.clan_buttons[3])
async def clan_settings(message: types.Message):
    """Настройки клана"""
    clan_info = await get_clan_info(message.from_user.id)
    await bot.send_message(message.from_user.id, strings.clan_settings_message,
                           reply_markup=await inline.clan_settings(clan_info.id))


@dp.callback_query_handler(UserInClan(), IsClanHead(), text=["change-emoji", "change-title"])
async def change_in_clan(call: types.CallbackQuery):
    """Изменить эмодзи/Название"""
    action = call.data.split("-")[1]
    clan_info = await get_clan_info(call.from_user.id)
    if action == "emoji":
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=strings.clan_choice_emoji,
                                    reply_markup=await inline.select_emoji_clan(await DB.select_clan_emojies(),
                                                                                clan_info.current_emoji,
                                                                                await clan_info.get_aviable_emojies))
    else:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=strings.clan_change_title_message,
                                    reply_markup=await inline.change_clan_title())


@dp.callback_query_handler(UserInClan(), IsClanHeadOrAdmin(), text_startswith="clan_req")
async def clan_request(call: types.CallbackQuery):
    """Принять/Отклонить запрос на вступление в клан"""
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=None)
    action = call.data.split("-")[1]
    user_id = int(call.data.split("-")[2])
    user_info = await get_user_info(user_id)

    try:
        clan_info = await get_clan_info(call.from_user.id)
    except TypeError:
        return

    if user_info.clan is None:
        if action == "accept":
            if await clan_info.get_clan_users_count(True) < config.CLAN_USERS_COUNT:
                await DB.delete_clan_invite_join(user_id)
                await DB.delete_clan_invite(user_id, await user_info.get_clan_invites, 0, True)

                await DB.add_user_to_clan(clan_info.name, user_id)

                await bot.send_message(call.from_user.id,
                                       strings.clan_req_accepted.format(await user_info.get_href_without_hp()))
                await bot.send_message(user_id, strings.you_was_accepted_to_clan.format(await clan_info.get_clan_title))

            else:
                await bot.send_message(call.from_user.id, strings.clan_count_users_is_too_much)
        else:
            await bot.send_message(call.from_user.id,
                                   strings.clan_req_declined.format(await clan_info.get_clan_title))
            await bot.send_message(user_id, strings.you_was_declined_to_clan.format(await clan_info.get_clan_title))

            await DB.delete_clan_invite_join(user_id)


@dp.callback_query_handler(UserNotInClan(), text_startswith="clan_inv")
async def accept_decline_invite(call: types.CallbackQuery):
    """Принять/Отклонить приглашение"""
    action = call.data.split("-")[1]
    clan_id = int(call.data.split("-")[2])
    user_info = await get_user_info(call.from_user.id)

    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=None)

    try:
        clan_info = Clan(*await DB.get_clan_info_with_clan_id(clan_id))
    except TypeError:
        return

    if action == "accept":
        if user_info.clan is None:
            if await clan_info.get_clan_users_count(True) < config.CLAN_USERS_COUNT:

                await DB.delete_clan_invite(call.from_user.id, await user_info.get_clan_invites, clan_id, True)
                await DB.delete_clan_invite_join(call.from_user.id)

                await DB.add_user_to_clan(clan_info.name, call.from_user.id)

                await bot.send_message(call.from_user.id,
                                       strings.clan_invite_accepted.format(await clan_info.get_clan_title))
                await ret_city(call.from_user.id)

            else:
                await bot.send_message(call.from_user.id, strings.clan_count_users_is_too_much)

        else:
            await bot.send_message(call.from_user.id, strings.you_already_in_clan)


    else:
        await bot.send_message(call.from_user.id, strings.clan_invite_declined.format(await clan_info.get_clan_title))
        await DB.delete_clan_invite(call.from_user.id, await user_info.get_clan_invites, clan_id, False)


@dp.callback_query_handler(UserInClan(), IsClanHead(), text_startswith="change_clan_title")
async def change_clan_title(call: types.CallbackQuery):
    """Сменить название клана -> да/нет"""
    action = call.data.split("-")[1]
    if action == "yes":
        user_info = await get_user_info(call.from_user.id)
        if user_info.gold > config.CHANGE_CLAN_TITLE_COST:
            await DB.update_balance(config.CHANGE_CLAN_TITLE_COST, "+", call.from_user.id)
            await bot.send_message(call.from_user.id, strings.clan_creation_requirements, reply_markup=await default.get_fight_res_button(
                strings.cancel_del))
            await ClanSettings.title.set()
        else:
            await call.answer(strings.get_you_cant_buy_it.format(user_info.gold))
    else:
        clan_info = await get_clan_info(call.from_user.id)
        await bot.edit_message_text(chat_id=call.from_user.id, text=strings.clan_settings_message,
                                    reply_markup=await inline.clan_settings(clan_info.id),
                                    message_id=call.message.message_id)


@dp.callback_query_handler(UserNotInClan(), text_startswith="send_req")
@dp.message_handler(UserNotInClan(), IsPrivate(), text_startswith="/clan_req")
async def clan_req(message_or_call):
    if isinstance(message_or_call, types.Message):
        return await send_req_to_clan(message_or_call.from_user.id, message_or_call.text)
    return await send_req_to_clan(message_or_call.from_user.id, message_or_call.data)


async def send_req_to_clan(user_id, data: str):
    user_info = await get_user_info(user_id)
    if user_info.clan is None:
        if user_info.clan_invite_join is None:
            try:
                clan_id = int(data.split("_")[2])
                clan_info = Clan(*await DB.get_clan_info_with_clan_id(clan_id))
            except (ValueError, TypeError):
                return await bot.send_message(user_id, strings.clan_is_not_have)

            if await clan_info.get_clan_users_count(True) < config.CLAN_USERS_COUNT:
                await DB.set_invites_join(user_id, clan_id)
                await bot.send_message(user_id, strings.you_send_invite_to_clan.format(await clan_info.get_clan_title))
                await ret_city(user_id)

            else:
                await bot.send_message(user_id, strings.clan_count_users_is_too_much)

        else:
            await bot.send_message(user_id, strings.you_already_have_invite_join)

    else:
        await bot.send_message(user_id, strings.you_already_in_clan)


@dp.message_handler(IsPrivate(), UserNotInClan(), text=strings.clan_default_buttons[2])
async def cancel_request(message: types.Message):
    """❌ Отменить заявку"""
    user_info = await get_user_info(message.from_user.id)

    if user_info.clan_invite_join is not None:
        clan_info = Clan(*await DB.get_clan_info_with_clan_id(user_info.clan_invite_join))
        await bot.send_message(message.from_user.id,
                               strings.clan_req_is_canceled.format(await clan_info.get_clan_title))
        await DB.set_invites_join(message.from_user.id, None)
        await ret_city(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, strings.clan_req_is_not_have)


@dp.message_handler(IsPrivate(), UserInClan(), IsClanHeadOrAdmin(), text=strings.control_clan_invites_buttons[0])
async def control_invites(message: types.Message):
    """📬 Управление приглашениями"""
    await bot.send_message(message.from_user.id, strings.clan_control_message,
                           reply_markup=await default.clan_controll())


@dp.message_handler(IsPrivate(), UserInClan(), IsClanHeadOrAdmin(), text=strings.control_clan_invites_buttons[2])
async def send_invite_to_clan(message: types.Message):
    """🗞 Отправить приглашение"""
    await bot.send_message(message.from_user.id, strings.clan_send_invite, reply_markup=await inline.find_user())


@dp.callback_query_handler(UserInClan(), IsClanHeadOrAdmin(), text_startswith="send_invite")
async def send_invite_inline(call: types.CallbackQuery):
    user_clan = await get_clan_info(call.from_user.id)
    if await user_clan.get_clan_users_count(True) < config.CLAN_USERS_COUNT:
        user_to_invite = int(call.data.split('-')[1])
        user_invite_info = await get_user_info(user_to_invite)
        if user_invite_info.clan is None:
            if user_clan.id not in await user_invite_info.get_clan_invites:
                await DB.add_clan_invites(user_clan.id, user_to_invite)
                await bot.send_message(call.from_user.id, strings.clan_invite_sended.format(
                    await user_invite_info.get_href_without_hp()))
                await ret_city(call.from_user.id)
            else:
                await bot.send_message(call.from_user.id, strings.cant_you_before_send_invite)

        else:
            return await bot.send_message(call.from_user.id, strings.not_can_send_invite)

    else:
        return await bot.send_message(call.from_user.id, strings.clan_count_users_is_too_much)
