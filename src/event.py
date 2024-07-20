from AzeibarjanWarBOT.utils import strings


class Event:
    def __init__(self, name, description, resources, gold, coupons):
        self.name = name
        self.description = description
        self.resources = resources
        self.gold = gold
        self.coupons = coupons


    async def get_event_description(self):
        return (f"\n"
                f"<b>{strings.event}</b>\n"
                f"\n"
                f"{self.name}\n"
                f"\n"
                f"{self.description}\n"
                f"\n"
                f"{strings.event_info_desc}\n"
                f"\n"
                f"{strings.event_rewards}\n"
                f"{await self.__get_items_desc()}\n")

    async def __get_items_desc(self):
        from AzeibarjanWarBOT.utils.class_getter import get_resource
        resources_list = []
        for res in self.resources.split():
            data_res = res.split("-")
            current_resource = await get_resource(data_res[0])
            resources_list.append(current_resource.title + f" x{data_res[1]}")
        if int(self.coupons):
            resources_list.append(strings.hero_item_list[1] + str(self.coupons))
        if int(self.gold):
            resources_list.append(strings.hero_item_list[0] + str(self.gold))

        return "\n".join(resources_list) if len(resources_list) else ""




