from AzeibarjanWarBOT.utils import strings


class Enemy:
    def __init__(self, id, name, description, lvl, max_hp, min_damage, max_damage, location, get_xp, get_gold, get_loot: str):
        self.id = id
        self.name = name
        self.description = description
        self.lvl = lvl
        self.max_hp = max_hp
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.location = location
        self.get_xp = get_xp
        self.get_gold = get_gold
        self.get_loot: list = get_loot.split()

    @property
    async def get_enemy_desc(self):
        from AzeibarjanWarBOT.src.dicts import transitions_v2

        from AzeibarjanWarBOT.utils.class_getter import get_resource
        resultat = []
        for item in self.get_loot:
            resource = await get_resource(item)
            resultat.append(resource.title)

        text = f"<b>{self.name}</b>\n" \
               f"{strings.mob_desc_zona_hunt} {transitions_v2[self.location]}\n" \
               f"{strings.hero_item_list[2]} {self.lvl}\n\n" + strings.enemy_drop.format(self.get_xp, self.get_gold, "\n".join(resultat))
        return text






