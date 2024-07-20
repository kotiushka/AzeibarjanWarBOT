from AzeibarjanWarBOT.utils import strings


class Quests:
    def __init__(self, id, quest_type_req, title, description, required, reward_xp, reward_gold, lvl):
        self.id = id
        self.quest_type_req = quest_type_req
        self.title = title
        self.description = description
        self.required = required
        self.reward_xp = reward_xp
        self.reward_gold = reward_gold
        self.lvl = lvl

    async def get_quest_description(self, required=0):
        return f"""
<b>{self.title}</b> ({0 if required is None else required}/{self.required})

{self.description}

{strings.quest_reward}
{strings.hero_item_list[0]}{self.reward_gold}
{strings.hero_item_list[3]}{self.reward_xp}"""







