from AzeibarjanWarBOT.utils import strings


class Resource:
    def __init__(self, id, item_id, title, type, rarity, description, quality, cost):
        self.id = id
        self.item_id = item_id
        self.title = title
        self.type = type
        self.rarity = rarity
        self.description = description
        self.quality = quality
        self.cost = cost

    @property
    async def get_desc(self):
        return f"{self.title}\n" \
               f"{self.description}"

    async def get_item_description_full(self, sale=0, symbol="💰"):
        return f"""
<b>{self.title}</b>

{strings.waepon_info_list[0]}{strings.resource}
{strings.waepon_info_list[2]}{self.quality}
{strings.waepon_info_list[3]}{self.rarity}

{strings.waepon_info_list[4]}

{self.description}

{strings.waepon_info_list[12]}{symbol}{int(self.cost - ((self.cost * sale) / 100))}"""

    async def crafter_description(self, count=0):
        text_count = f" - {count}{strings.count}" if count else ""

        return f"\n<b>{self.title} {self.quality} </b> {text_count}\n{strings.instruction}"

    async def potion_description(self, count=0):
        text_count = f" - {count}{strings.count}" if count else ""

        return f"\n<b>{self.title} {self.quality}</b> {text_count}\n{self.description}\n\n" \
               f"{strings.for_use} /use_{self.item_id}\n"

    async def default_description(self, count=0):
        text_count = f" - {count}{strings.count}" if count else ""
        return f"\n<b>{self.title}</b> {text_count}\n" \
               f"{self.description.format(self.id)}\n"





