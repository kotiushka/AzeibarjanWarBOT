from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import default, inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.src import dicts
from AzeibarjanWarBOT.state import states
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_user_info, get_trade_room
from AzeibarjanWarBOT.utils.functions import ret_city

cb_next = CallbackData("next", "move")
cb_back = CallbackData("back", "move")
cb_item_click = CallbackData("item", "click")


@dp.message_handler(IsPrivate(), text=strings.menu_chield_buttons_text[2])
async def trade_text(message: types.Message):
    """Отправляет меню поиска юзера для торговли"""
    await bot.send_message(message.from_user.id, strings.trade_message, reply_markup=await inline.find_user())


@dp.callback_query_handler(text_startswith="offer")
async def offer_trade(call: types.CallbackQuery):
    """Отправка сообщения об предложении торговли"""
    user_info_to_trade = await get_user_info(int(call.data.split("-")[1]))
    user_info = await get_user_info(call.from_user.id)
    if user_info_to_trade.city == user_info.city:
        # Пишем что предложение об торговле было отправлено
        await bot.send_message(call.from_user.id, strings.offer_sended)
        await ret_city(call.from_user.id)
        # Пишем человеку которому адресована торговля что пришёл запрос
        text = f"{strings.invite_to_offer[0]} {await user_info.get_href_without_hp()} - {strings.invite_to_offer[1]}"
        await bot.send_message(user_info_to_trade.id, text, reply_markup=await inline.accept_or_no_trade(user_info.id))

    else:
        await bot.send_message(call.from_user.id, strings.user_not_in_your_location)


@dp.callback_query_handler(text_startswith=["accept", "decline"])
async def offer_accepting(call: types.CallbackQuery):
    """Реакция на нажатие принять или отклонить предложение об трейде"""
    data = call.data.split("-")
    user_info_to_trade = await get_user_info(int(data[1]))
    user_info = await get_user_info(call.from_user.id)

    # Удалим reply_markup
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=None)

    if user_info_to_trade.city == user_info.city:
        if data[0] == "accept":
            if not await DB.get_bool_npcRoom(user_info_to_trade.id) and not await DB.get_bool_tradeRoom(user_info_to_trade.id):
                # Запустим стейт торговли
                await set_state_for_user(call.from_user.id, states.Trade.trade)
                await set_state_for_user(user_info_to_trade.id, states.Trade.trade)

                # Добавим в БД меню трейда
                await DB.create_trade_room(call.from_user.id, user_info_to_trade.id)

                # Отправим что торговля началась
                await bot.send_message(call.from_user.id,
                                       f"{strings.invite_to_offer[2]} {await user_info_to_trade.get_href_without_hp()}",
                                       reply_markup=await default.get_fight_res_button(strings.cancel_trading))
                await bot.send_message(user_info_to_trade.id,
                                       f"{strings.invite_to_offer[2]} {await user_info.get_href_without_hp()}",
                                       reply_markup=await default.get_fight_res_button(strings.cancel_trading))

                # Отправим меню торговли
                await bot.send_message(call.from_user.id, strings.choise_for_offer,
                                       reply_markup=await inline.trade_buttons())
                await bot.send_message(user_info_to_trade.id, strings.choise_for_offer,
                                       reply_markup=await inline.trade_buttons())

            else:
                await bot.send_message(call.from_user.id, strings.invite_to_offer[5])

        else:
            # Отправим что торговля была отменена
            await bot.send_message(call.from_user.id, strings.invite_to_offer[3])
            await bot.send_message(user_info_to_trade.id,
                                   f"{await user_info_to_trade.get_href_without_hp()} {strings.invite_to_offer[4]}")

    else:
        # Если игрок уже в другом городе
        await bot.send_message(call.from_user.id, strings.user_not_in_your_location)


@dp.message_handler(IsPrivate(), state=states.Trade.trade)
async def trade(message: types.Message):
    """Ловим все сообщения в трейде"""
    trade_room = await get_trade_room(message.from_user.id)
    if message.text == strings.cancel_trading:
        await bot.send_message(message.from_user.id, strings.trade_canceled)
        await ret_city(message.from_user.id)

        user_to_trade_id = await trade_room.get_trade_user_id(message.from_user.id)
        user_in_trade = await get_user_info(trade_room.user_1) if user_to_trade_id != 1 else await get_user_info(
            trade_room.user_2)

        await bot.send_message(user_in_trade.id,
                               f"{await user_in_trade.get_href_without_hp()} {strings.trade_canceled_user_2}")
        await ret_city(user_in_trade.id)

        await reset_state_for_user(message.from_user.id)
        await reset_state_for_user(user_in_trade.id)

        await trade_room.revert_trade()
        await DB.delete_trade_room(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, strings.there_is_a_trade,
                               reply_markup=await default.get_fight_res_button(strings.cancel_trading))


@dp.callback_query_handler(text="resources_offer", state=states.Trade.trade)
async def trade_resources(call: types.CallbackQuery):
    """Нажатие на кнопку ресурсов в трейде"""
    user_info = await get_user_info(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=strings.choise_which_resouser_trade,
                                reply_markup=await inline.resources_keyboard(user_info.nickname, True))


@dp.callback_query_handler(text="equip_offer", state=states.Trade.trade)
async def trade_equip(call: types.CallbackQuery):
    """Нажатие на кнопку экипировки в трейде"""
    user_info = await get_user_info(call.from_user.id)
    array = await DB.get_current_items(user_info.nickname, "", False)

    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=strings.choise_which_equip_trade,
                                reply_markup=await inline.list_keyboard(array, 0, 5, cb_next, cb_back,
                                                                        cb_item_click, True, "back_to_offer"))


@dp.callback_query_handler(text_endswith="_trade", state=states.Trade.trade)
async def trade_resource_more(call: types.CallbackQuery):
    """Нажатие на кнопку одна из которых предложена после выбора ресурсов в трейде"""
    user_info = await get_user_info(call.from_user.id)
    res_type = call.data.split("_")[0]
    array = await DB.get_current_items(user_info.nickname, res_type)

    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=await inline.list_keyboard(array, 0, 5, cb_next, cb_back,
                                                                                cb_item_click, True, "resources_offer"))


@dp.callback_query_handler(text=["gold_offer", "coupons_offer"], state=states.Trade.trade)
async def trade_gold(call: types.CallbackQuery):
    """Нажатие на кнопку золота или купонов в трейде"""
    user_info = await get_user_info(call.from_user.id)
    if call.data == "gold_offer":
        cb = "gold"
        text = strings.how_much_gold_trade.format(user_info.gold)
    else:
        cb = "coupon"
        text = strings.how_much_coupon_trade.format(user_info.coupon)

    await bot.edit_message_text(chat_id=call.from_user.id, text=text, message_id=call.message.message_id,
                                reply_markup=await inline.gold_coupon_trade_buttons(cb))


@dp.callback_query_handler(text_startswith=["gold_offer_", "coupon_offer_"], state=states.Trade.trade)
async def coupon_gold_action(call: types.CallbackQuery):
    """Обработка нажатия на монеты или купоны чтобы добавить в трейд"""
    data = call.data.split("_")
    currency_type = data[0]
    value = int(data[2])

    user_info = await get_user_info(call.from_user.id)
    trade_info = await get_trade_room(call.from_user.id)
    user_trade_id = await trade_info.get_trade_user_id(call.from_user.id)
    user_balance = user_info.coupon if currency_type == "coupon" else user_info.gold

    if user_balance >= value:
        # Добавим валюту в трейд
        await DB.update_coupon_gold(call.from_user.id, user_trade_id, currency_type, value)
        # Обновим баланс
        await DB.update_balance(value, "-", call.from_user.id) if currency_type == "gold" else await DB.update_balance(
            value, "-", call.from_user.id, True)
        # Успешно добавлено {} {} в трейд
        await call.answer(strings.successfull_add_currency.format(value, "💰" if currency_type == "gold" else "🎫"))
        # Вернем меню трейда
        trade_info = await get_trade_room(call.from_user.id)
        await bot.edit_message_text(chat_id=call.from_user.id, text=await trade_info.get_text_trade(call.from_user.id),
                                    message_id=call.message.message_id,
                                    reply_markup=await inline.trade_buttons())
    else:
        await call.answer(strings.not_enough_currency)


@dp.callback_query_handler(cb_item_click.filter(), state=states.Trade.trade)
async def item_button(call: types.CallbackQuery):
    """Реагирем на кнопку выбора определенного ресурса или экипировки"""
    data = call.data.split(":")[1].split("-")
    user_info = await get_user_info(call.from_user.id)
    current_item_info = await DB.get_current_item_from_inventory(user_info.nickname, data[1])
    trade_info = await get_trade_room(call.from_user.id)

    user_trade_id = await trade_info.get_trade_user_id(call.from_user.id)
    item_type = "equip" if current_item_info[2] in dicts.equip_types else "resources"

    await DB.add_equip_res(call.from_user.id, user_trade_id, item_type,
                           f"{current_item_info[3]}-{current_item_info[5]}")
    await DB.delete_from_inventory(current_item_info[0], user_info.nickname)

    await call.answer(strings.successfull_add_to_trade)
    trade_info = await get_trade_room(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id, text=await trade_info.get_text_trade(call.from_user.id),
                                message_id=call.message.message_id,
                                reply_markup=await inline.trade_buttons())


@dp.callback_query_handler(cb_next.filter(), state=states.Trade.trade)
async def nextButtons(call: types.CallbackQuery):
    """Кнопка назад (стрелочки)"""
    if call.data.split(":")[1].split("-")[-1] not in dicts.equip_types:
        await move_item(call, True, "resources_offer", True)
    else:
        await move_item(call, True, "back_to_offer", False)


@dp.callback_query_handler(cb_back.filter(), state=states.Trade.trade)
async def previoslyButtons(call: types.CallbackQuery):
    """Кнопка вперед (стрелочки)"""
    if call.data.split(":")[1].split("-")[-1] not in dicts.equip_types:
        await move_item(call, False, "resources_offer", True)
    else:
        await move_item(call, False, "back_to_offer", False)


@dp.callback_query_handler(text="back_to_offer", state=states.Trade.trade)
async def trade_back(call: types.CallbackQuery):
    """Кнопка назад чтобы вернутся к меню трейда"""
    trade_room = await get_trade_room(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id, text=await trade_room.get_text_trade(call.from_user.id),
                                message_id=call.message.message_id,
                                reply_markup=await inline.trade_buttons())


async def move_item(call: types.callback_query, is_next, button_back, is_res):
    """Функция которая обрабатывает кнопку вперед или назад"""
    data = call.data.split(":")[1].split("-")
    first_num, last_num = map(int, data[:2])
    list_name = data[2]

    user_info = await get_user_info(call.from_user.id)

    array = await DB.get_current_items(user_info.nickname, list_name, is_res)

    if not is_next:
        if last_num - 5 > 0:
            await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                reply_markup=await inline.list_keyboard(array, first_num - 5,
                                                                                        last_num - 5,
                                                                                        cb_next, cb_back, cb_item_click,
                                                                                        True, button_back))
        else:
            await call.answer(strings.first_page)
    else:
        for i in range(5, 1, -1):
            if not i + first_num > len(array) and i + first_num != len(array):
                return await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                    reply_markup=await inline.list_keyboard(array, first_num + i,
                                                                                            last_num + 5,
                                                                                            cb_next, cb_back,
                                                                                            cb_item_click, True,
                                                                                            button_back))
            else:
                return await call.answer(strings.last_page)



@dp.callback_query_handler(text="accept_actions_offer", state=states.Trade.trade)
async def trade_accept_res(call: types.CallbackQuery):
    """Кнопка подтвердить в трейде"""
    trade_info = await get_trade_room(call.from_user.id)
    user_trade_id = await trade_info.get_trade_user_id(call.from_user.id)

    user_in_trade = await get_user_info(trade_info.user_1) if user_trade_id != 1 else await get_user_info(
        trade_info.user_2)
    user_info = await get_user_info(call.from_user.id)
    main_user_title = await user_info.get_href_without_hp()

    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=None)

    await DB.set_ready_offer(call.from_user.id, user_trade_id, 1)

    if user_trade_id == 1 and trade_info.ready_2 < 1 or user_trade_id != 1 and trade_info.ready_1 < 1:
        await bot.send_message(call.from_user.id, strings.you_confirmed_to_offer)
        await bot.send_message(user_in_trade.id, strings.user_confirm_offer_ready.format(main_user_title))

    else:
        second_user_title = await user_in_trade.get_href_without_hp()
        text = f"{strings.menu_chield_buttons_text[2]}\n\n" \
               f"{strings.user_offers.format(main_user_title)}\n\n" \
               f"{await trade_info.get_text_trade(call.from_user.id, False)}\n\n" \
               f"{strings.user_offers.format(second_user_title)}\n\n" \
               f"{await trade_info.get_text_trade(user_in_trade.id, False)}"

        await bot.send_message(call.from_user.id, text=text, reply_markup=await inline.offer_result_buttons(trade_info.id))
        await bot.send_message(user_in_trade.id, text=text, reply_markup=await inline.offer_result_buttons(trade_info.id))


@dp.callback_query_handler(text_startswith="change_offer", state=states.Trade.trade)
async def go_changes(call: types.CallbackQuery):
    """Изменить в торговле"""
    trade_info = await get_trade_room(call.from_user.id)
    if int(call.data.split("-")[1]) == trade_info.id:

        user_in_trade = await get_user_info(trade_info.user_1) if await trade_info.get_trade_user_id(call.from_user.id) != 1 else await get_user_info(trade_info.user_2)
        user_info = await get_user_info(call.from_user.id)
        user_in_trade_ready = trade_info.ready_1 if user_in_trade.id == trade_info.user_1 else trade_info.ready_2

        if user_in_trade_ready == 2:
            await DB.set_ready_offer(user_in_trade.id, await trade_info.get_trade_user_id(user_in_trade.id), 1)

        await DB.set_ready_offer(call.from_user.id, await trade_info.get_trade_user_id(call.from_user.id), 0)

        await bot.edit_message_text(chat_id=call.from_user.id, text=await trade_info.get_text_trade(call.from_user.id),
                                    message_id=call.message.message_id,
                                    reply_markup=await inline.trade_buttons())
        await bot.send_message(user_in_trade.id, strings.go_changes_offer.format(await user_info.get_href_without_hp()))

    else:
        await bot.send_message(call.from_user.id, strings.trade_is_disabled)


@dp.callback_query_handler(text_startswith="agree_offer", state=states.Trade.trade)
async def accept_offer(call: types.callback_query):
    trade_info = await get_trade_room(call.from_user.id)

    if int(call.data.split("-")[1]) == trade_info.id:
        user_1_trade_id = await trade_info.get_trade_user_id(call.from_user.id)
        user_2_trade_id = 2 if user_1_trade_id == 1 else 1

        user_in_trade = await get_user_info(trade_info.user_2) if trade_info.user_2 != call.from_user.id else await get_user_info(trade_info.user_1)
        user_info = await get_user_info(call.from_user.id)

        await DB.set_ready_offer(call.from_user.id, user_1_trade_id, 2)

        await bot.send_message(call.from_user.id, strings.user_confirm_offer_resultat.format(await user_info.get_href_without_hp()))
        await bot.send_message(user_in_trade.id, strings.user_confirm_offer_resultat.format(await user_info.get_href_without_hp()))

        trade_info = await get_trade_room(call.from_user.id)
        ready_in_trade_user = trade_info.ready_1 if user_2_trade_id == 1 else trade_info.ready_2

        if ready_in_trade_user == 2:
            for user in [call.from_user.id, user_in_trade.id]:
                await reset_state_for_user(user)
                await bot.send_message(user, strings.offer_successfully_end)
                await ret_city(user)
            await trade_info.revert_trade(True)
            await DB.delete_trade_room(call.from_user.id)

        elif ready_in_trade_user == 0:
            await bot.send_message(call.from_user.id, strings.wait_while_user_2_go_changes)
    else:
        await bot.send_message(call.from_user.id, strings.trade_is_disabled)

async def set_state_for_user(user_id, state: FSMContext) -> None:
    """Функция для запуска стейта"""
    context = dp.current_state(chat=user_id, user=user_id)
    await context.set_state(state)


async def reset_state_for_user(user_id) -> None:
    """Функция для удаления стейта"""
    context = dp.current_state(chat=user_id, user=user_id)
    await context.reset_state()
