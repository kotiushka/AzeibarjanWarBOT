from aiogram import types
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.filters.filter import IsPrivate
from AzeibarjanWarBOT.keyboards import inline
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings, functions
from AzeibarjanWarBOT.utils.class_getter import get_quest, get_user_info


@dp.callback_query_handler(text="back_to_quests")
@dp.message_handler(IsPrivate(), text=strings.menuMainButtonsList[4])
async def quests(message_or_call):
    """city quests"""
    if isinstance(message_or_call, types.Message):
        await bot.send_message(message_or_call.from_user.id, text="Квесты на сегодня:", reply_markup=await inline.quest_buttons(message_or_call.from_user.id))
    elif isinstance(message_or_call, types.CallbackQuery):
        await bot.edit_message_text(chat_id=message_or_call.from_user.id, text="Квесты на сегодня:", reply_markup=await inline.quest_buttons(message_or_call.from_user.id), message_id=message_or_call.message.message_id)


@dp.callback_query_handler(text_startswith=["quest-accept", "quest-decline"])
async def quest_accept_decline(call: types.CallbackQuery):
    data = call.data.split("-")
    quest_id = int(data[2])
    if data[1] == "accept":
        await DB.add_quest_users(call.from_user.id, quest_id)
        await call.answer(strings.quest_taked)
    else:
        await DB.delete_quest_users(call.from_user.id, quest_id)
        await call.answer(strings.quest_canceled)

    await bot.edit_message_text(chat_id=call.from_user.id, text="Квесты на сегодня:", reply_markup=await inline.quest_buttons(call.from_user.id), message_id=call.message.message_id)


@dp.callback_query_handler(text_startswith="quest-reward")
async def take_quest_reward(call: types.CallbackQuery):
    """take quest_reward"""
    quest_id = int(call.data.split("-")[2])
    user_quest = await DB.get_quest_user_received(call.from_user.id, quest_id)
    if user_quest is not None:
        current_quest = await get_quest(quest_id)
        if not await DB.get_succes_quest(call.from_user.id, quest_id):
            if user_quest == current_quest.required:
                user_info = await get_user_info(call.from_user.id)

                gold_add = current_quest.reward_gold
                lvl_boost = current_quest.reward_xp

                lvl_boost = round(lvl_boost + lvl_boost / 100 * user_info.bonus_xp if user_info.bonus_xp != 0 else lvl_boost)
                gold_add = round(gold_add + gold_add / 100 * user_info.bonus_gold if user_info.bonus_gold != 0 else gold_add)

                await DB.update_balance(gold_add, "+", call.from_user.id)
                await functions.increase_player_level(user_info, lvl_boost)
                await DB.change_succes_quest(call.from_user.id, quest_id)

                await bot.edit_message_text(
                    chat_id=call.from_user.id,
                    text=strings.get_received_reward.format
                    (
                        lvl_boost,
                        f"(+{user_info.bonus_xp}%)" if user_info.bonus_xp != 0 else "",
                        gold_add, f"(+{user_info.bonus_gold}%)" if user_info.bonus_gold != 0 else "",
                        ""
                    ),
                    message_id=call.message.message_id
                )
        else:
            await call.answer(strings.you_getted_reward_quest)

@dp.callback_query_handler(text_startswith="quest-")
async def quest_button(call: types.CallbackQuery):
    """tap to inline quest button"""
    quest = await get_quest(call.data.split("-")[1])
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                text=await quest.get_quest_description(await DB.get_quest_user_received(call.from_user.id, quest.id)),
                                reply_markup=await inline.quest_tap_buttons(call.from_user.id, quest.id))
