from aiogram.dispatcher.filters.state import StatesGroup, State


class StartState(StatesGroup):
    course = State()
    name = State()


class MapState(StatesGroup):
    cancel_go = State()

class FightState(StatesGroup):
    cancel_find = State()
    fight_attack = State()
    fight_defence = State()


class DeleteHero(StatesGroup):
    delete_hero = State()

class ChangeStatistic(StatesGroup):
    change_name = State()
    change_course = State()


class Trade(StatesGroup):
    trade = State()


class CreateClan(StatesGroup):
    create = State()
    choice_emoji = State()


class ClanSettings(StatesGroup):
    title = State()



class Admin(StatesGroup):
    add_event = State()

class FightStateUser(StatesGroup):
    cancel_find = State()
    fight_attack = State()
    fight_defence = State()

