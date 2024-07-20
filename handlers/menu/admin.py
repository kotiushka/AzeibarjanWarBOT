from aiogram import types
from aiogram.dispatcher import FSMContext

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.state.states import Admin
from AzeibarjanWarBOT.filters.filter import IsPrivate, IsAdmin
from AzeibarjanWarBOT.keyboards import default
from AzeibarjanWarBOT.loader import dp, bot
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_resource


@dp.message_handler(IsPrivate(), IsAdmin(), text=strings.admin_button)
async def admin_panel(message: types.Message):
    await bot.send_message(message.from_user.id, "👑 <b>Привет, админ!</b>", reply_markup=await default.admin_menu())


@dp.message_handler(IsPrivate(), IsAdmin(), text=strings.admin_buttons[0])
async def change_event(message: types.Message, state: FSMContext):
    await Admin.add_event.set()
    await state.update_data(name="", desc="", resources="", gold=0, coupons=0)
    await bot.send_message(message.from_user.id, await get_event_desc(state), reply_markup=await default.change_event_menu())


@dp.message_handler(IsPrivate(), IsAdmin(), text=strings.change_event_buttons[0], state=Admin.add_event)
async def check_event_buttons(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, await get_event_desc(state))


@dp.message_handler(IsPrivate(), IsAdmin(), text=strings.change_event_buttons[1], state=Admin.add_event)
async def command_list(message: types.Message):
    resultat = [f"<code>/e-add-{resource[0]} 1</code> - {resource[1]}" for resource in await DB.get_resources_list()]
    resultat.append("<code>/e-set-title название</code> - Изменить название")
    resultat.append("<code>/e-set-desc описание</code> - Изменить описание")
    resultat.append("<code>/e-set-gold 100</code> - Добавить монеты")
    resultat.append("<code>/e-set-coupons 1</code> - Добавить купоны")
    await bot.send_message(message.from_user.id, "\n".join(resultat))


@dp.message_handler(IsPrivate(), IsAdmin(), text_startswith=["/e-set", "/e-add"], state=Admin.add_event)
async def set_gold_coupon(message: types.Message, state: FSMContext):
    try:
        action_type = message.text.split("-")[1]
        item = message.text.split("-")[2].split()[0]
        value = message.get_args()
        if action_type == "set":
            if item == "gold":
                await state.update_data(gold=int(value))
            elif item == "coupons":
                await state.update_data(coupons=int(value))
            elif item == "title":
                await state.update_data(name=value)
            elif item == "desc":
                await state.update_data(desc=value)
        elif action_type == "add":
            state_data = await state.get_data()
            await state.update_data(resources=state_data["resources"] + f" {item}-{value}")

        await bot.send_message(message.from_user.id, "Успешно изменено!")
        await bot.send_message(message.from_user.id, await get_event_desc(state), reply_markup=await default.change_event_menu())
    except ValueError:
        await bot.send_message(message.from_user.id, "Неверный тип команды.")



@dp.message_handler(IsPrivate(), IsAdmin(), text=strings.change_event_buttons[3], state=Admin.add_event)
async def event_creating_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data["name"] != "" and data["desc"] != "":
        await DB.create_event(data)
        await state.finish()
        await bot.send_message(message.from_user.id, "Создание события было успешно!", reply_markup=await default.admin_menu())
        await DB.set_event_reward(1, 0, True)
    else:
        await bot.send_message(message.from_user.id, "Поле названия или описания не были заполнены!")




@dp.message_handler(IsPrivate(), IsAdmin(), text=strings.cancel_del, state=Admin.add_event)
async def cancel_change_event(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id, "Создание события успешно отменено.", reply_markup=await default.admin_menu())

async def get_event_desc(state: FSMContext):
    data = await state.get_data()
    return f"<b>Название события</b>: {data['name']}\n" + \
        f"<b>Описание события</b>: {data['desc']}\n\n" + \
        "<b>Подарки события</b>:\n" + \
        f"<b>Ресурсы:</b> {await get_resources_text(data['resources'])}\n" + \
        f"<b>Золото:</b> {data['gold']}\n" + \
        f"<b>Купоны:</b> {data['coupons']}\n"


async def get_resources_text(data: str):
    text = ""
    for resource in data.split():
        resource = resource.split("-")
        resource_info = await get_resource(resource[0])
        text += f"\n{resource_info.title} x{resource[1]}"
    return text


