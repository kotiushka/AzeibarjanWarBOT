from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.utils import strings
from AzeibarjanWarBOT.utils.class_getter import get_resource, get_user_info, get_item


class Craft:
    def __init__(self, id: int, city: str, type: int, covan_stall: int, hitin: int, buk: int, cuprum: int, wood: int,
                 bone: int, tin: int,
                 sosna: int, leather: int, chain: int, needle: int, web: int, brick: int, thread: int, magnete: int,
                 uran: int, potion: int, manganese: int, boar_meat: int, dog_meat: int, salt: int, corn: int,
                 onion: int, garlic: int, sticks: int, unbrella: int, tear: int, resultat: str):
        self.id = id
        self.city = city
        self.type = type
        self.covan_stall = covan_stall
        self.hitin = hitin
        self.buk = buk
        self.cuprum = cuprum
        self.wood = wood
        self.bone = bone
        self.tin = tin
        self.sosna = sosna
        self.leather = leather
        self.chain = chain
        self.needle = needle
        self.web = web
        self.brick = brick
        self.thread = thread
        self.magnete = magnete
        self.uran = uran
        self.potion = potion
        self.manganese = manganese
        self.boar_meat = boar_meat
        self.dog_meat = dog_meat
        self.salt = salt
        self.corn = corn
        self.onion = onion
        self.garlic = garlic
        self.sticks = sticks
        self.unbrella = unbrella
        self.tear = tear
        self.resultat = resultat

    async def craft_item(self, user_id):
        user_info = await get_user_info(user_id)
        vrs = vars(self)
        for res in vrs:
            if res not in ["id", "city", "type", "resultat"] and vrs[res] != 0:
                await DB.delete_from_inventory_with_item_name(res, user_info.nickname, vrs[res])

        resultat_res = await get_item(self.resultat)
        await DB.add_item_to_inventory(user_info.nickname, resultat_res.type, resultat_res.id)


    async def check_can_craft(self, user_id):
        user_info = await get_user_info(user_id)
        vrs = vars(self)
        for res in vrs:
            if res not in ["id", "city", "type", "resultat"] and vrs[res] != 0:
                res_count = await DB.get_count_items_from_inventory(res, user_info.nickname, with_item_name=True)
                if res_count < vrs[res]:
                    return False
        return True

    async def get_description(self, user_id):
        result = strings.need_resouces_for_craft + "\n"
        vrs = vars(self)
        user_info = await get_user_info(user_id)
        for res in vrs:
            if res not in ["id", "city", "type", "resultat"] and vrs[res] != 0:
                res_count = await DB.get_count_items_from_inventory(res, user_info.nickname, with_item_name=True)
                current_resource = await get_resource(res)
                result += f"{vrs[res]}x - {current_resource.title} {'🔻' if res_count < vrs[res] else '✅'}\n"

        return result


