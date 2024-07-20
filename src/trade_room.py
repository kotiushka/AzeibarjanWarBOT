from AzeibarjanWarBOT.src.item import InventoryItem
from AzeibarjanWarBOT.src.resource import Resource
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.utils import strings


class TradeRoom:
    def __init__(self, id, user_1, user_2, gold_1, gold_2, coupons_1, coupons_2, equip_1, equip_2, resources_1,
                 resources_2, ready_1, ready_2):
        self.user_1 = user_1
        self.user_2 = user_2
        self.gold_1 = gold_1
        self.gold_2 = gold_2
        self.coupons_1 = coupons_1
        self.coupons_2 = coupons_2
        self.equip_1 = equip_1
        self.equip_2 = equip_2
        self.resources_1 = resources_1
        self.resources_2 = resources_2
        self.ready_1 = ready_1
        self.ready_2 = ready_2
        self.id = id

    async def get_user_data(self, trade_id):
        user_data = {
            self.user_1: {
                "gold": {"value": self.gold_1, "title": strings.hero_item_list[0]},
                "coupons": {"value": self.coupons_1, "title": strings.hero_item_list[1]},
                "equip": {"value": self.equip_1, "title": f"<b>{strings.hero_buttots_keyb[2]}</b>:"},
                "resources": {"value": self.resources_1, "title": f"<b>{strings.hero_buttots_keyb[3]}</b>:"}
            },
            self.user_2: {
                "gold": {"value": self.gold_2, "title": strings.hero_item_list[0]},
                "coupons": {"value": self.coupons_2, "title": strings.hero_item_list[1]},
                "equip": {"value": self.equip_2, "title": f"<b>{strings.hero_buttots_keyb[2]}</b>:"},
                "resources": {"value": self.resources_2, "title": f"<b>{strings.hero_buttots_keyb[3]}</b>:"}
            }
        }
        return user_data[self.user_1] if trade_id == 1 else user_data[self.user_2]

    async def get_text_trade(self, user_id, title=True) -> str:
        user_data = await self.get_user_data(await self.get_trade_user_id(user_id))
        resultat = [f"{strings.menu_chield_buttons_text[2]}\n\n{strings.you_offer_to_trade}"] if title else []
        for attr in user_data:
            current_attr = user_data[attr]
            if attr == "gold" or attr == "coupons":
                if current_attr["value"] != 0:
                    resultat.append(f"{current_attr['title']} {current_attr['value']}")
            else:
                if current_attr["value"] != "":
                    resultat.append(current_attr["title"])

                    for item in current_attr["value"].split():
                        item_id, item_up_lvl = item.split("-")[:]
                        try:
                            current_item = InventoryItem(*await DB.get_item(item_id))
                        except TypeError:
                            current_item = Resource(*await DB.get_resource(item_id))
                        if attr == "equip":
                            up_text = f"(+{item_up_lvl})" if item_up_lvl != "0" else ""
                            resultat.append(f"{current_item.title} {up_text}")
                        else:
                            resultat.append(f"{current_item.title}")

        if title:
            return "\n\n".join(resultat) if len(resultat) != 1 else "\n".join(resultat) + f"\n{strings.not_offers}"
        return "\n\n".join(resultat) if len(resultat) != 0 else f"{strings.not_offers}"

    async def revert_trade(self, suc_trade=False):
        item_list = [
            (self.gold_1, self.user_1, False), (self.gold_2, self.user_2, False),
            (self.coupons_1, self.user_1, True), (self.coupons_2, self.user_2, True)
        ] if not suc_trade else [
            (self.gold_1, self.user_2, False), (self.gold_2, self.user_1, False),
            (self.coupons_1, self.user_2, True), (self.coupons_2, self.user_1, True)
        ]

        for resource, user, is_coupon in item_list:
            await DB.update_balance(resource, "+", user, is_coupon)

        await self.__add_items_to_inv(self.user_1 if not suc_trade else self.user_2, suc_trade)
        await self.__add_items_to_inv(self.user_2 if not suc_trade else self.user_1, suc_trade)

    async def __add_items_to_inv(self, user_id, suc_trade: bool):
        user_info = User(*await DB.get_user_info(user_id))
        if not suc_trade:
            groups = [self.equip_1, self.resources_1] if user_id == self.user_1 else [self.equip_2, self.resources_2]
        else:
            groups = [self.equip_2, self.resources_2] if user_id == self.user_1 else [self.equip_1, self.resources_1]

        for group in groups:
            items = group.split()
            for item in items:
                item_id, item_up_lvl = item.split("-")[:]
                try:
                    current_item = InventoryItem(*await DB.get_item(item_id))
                    item_id = current_item.id
                except TypeError:
                    current_item = Resource(*await DB.get_resource(item_id))
                    item_id = current_item.item_id

                await DB.add_item_to_inventory(user_info.nickname, current_item.type, item_id, int(item_up_lvl))

    async def get_trade_user_id(self, user_id: int) -> int:
        """Функция получения айди юзера в трейде"""
        return 1 if self.user_1 == user_id else 2
