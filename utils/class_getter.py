from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.src.clan import Clan
from AzeibarjanWarBOT.src.enemy import Enemy
from AzeibarjanWarBOT.src.event import Event
from AzeibarjanWarBOT.src.fight_room import Fight
from AzeibarjanWarBOT.src.fight_room_u import FightRoomUsers
from AzeibarjanWarBOT.src.item import InventoryItem
from AzeibarjanWarBOT.src.locations import Location
from AzeibarjanWarBOT.src.quests import Quests
from AzeibarjanWarBOT.src.resource import Resource
from AzeibarjanWarBOT.src.trade_room import TradeRoom
from AzeibarjanWarBOT.src.trick import Trick
from AzeibarjanWarBOT.src.user import User


async def get_fight_room(user_id) -> Fight:
    res = await DB.get_fight_room_info(user_id)
    return Fight(*res)

async def get_location(location_id) -> Location:
    res = await DB.get_location(location_id)
    return Location(*res)

async def get_trick(trick_id) -> Trick:
    res = await DB.get_trick(trick_id)
    return Trick(*res)

async def get_user_info(user_id) -> User:
    res = await DB.get_user_info(user_id)
    return User(*res)

async def get_item(item_id) -> InventoryItem:
    res = await DB.get_item(item_id)
    return InventoryItem(*res)

async def get_enemy_list(current_location) -> list[Enemy]:
    res = await DB.get_enemy_list(current_location)
    return [Enemy(*i) for i in res]

async def get_resource(item_id) -> Resource:
    return Resource(*await DB.get_resource(item_id))

async def get_trade_room(user_id) -> TradeRoom:
    return TradeRoom(*await DB.get_trade_room(user_id))

async def get_clan_info(user_id) -> Clan:
    return Clan(*await DB.get_user_clan(user_id))

async def get_quest(quest_id) -> Quests:
    return Quests(*await DB.get_quest(quest_id))

async def get_event() -> Event:
    return Event(*await DB.get_event())

async def get_fight_room_u(user_id) -> FightRoomUsers:
    return FightRoomUsers(*await DB.get_fight_room_users(user_id))




