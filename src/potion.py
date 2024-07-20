import asyncio

from AzeibarjanWarBOT.database import DB
from AzeibarjanWarBOT.loader import bot
from AzeibarjanWarBOT.src.user import User
from AzeibarjanWarBOT.utils import strings


class Potion:
    def __init__(self, potion_id, up_hp_proc, up_xp_proc, up_regen_proc, up_gold_proc, duration):
        self.id = potion_id
        self.up_hp_proc = up_hp_proc
        self.up_xp_proc = up_xp_proc
        self.up_regen_proc = up_regen_proc
        self.up_gold_proc = up_gold_proc
        self.duration = duration

        self.effects = {
            "bonus_xp": up_xp_proc,
            "regen_hp": up_regen_proc,
            "current_hp": up_hp_proc,
            "bonus_gold": up_gold_proc
        }

    async def use_potion(self, user_info: User, potion_name):

        async def use_effects(operand):
            for eff in self.effects:
                if self.effects[eff]:
                    if eff not in user_info.current_potions:
                        if eff != "current_hp":
                            await DB.use_potion(user_info, [eff, self.effects[eff]], operand)
                        else:
                            await DB.use_potion(user_info, [eff, await self.get_proc_heal(user_info.id)], operand)

                        if operand != "-" and eff != "current_hp":
                            await DB.add_current_potion(eff, user_info.id)
                    else:
                        return True

        if not await use_effects("+"):
            await DB.delete_from_inventory_with_item_name(potion_name, user_info.nickname)

            await bot.send_message(user_info.id, await self.get_potion_result(user_info.id))

            await asyncio.sleep(self.duration * 60)

            return await use_effects("-")

        await bot.send_message(user_info.id, strings.effect_been_used)

    async def get_proc_heal(self, user_id) -> int:
        user_info = User(*await DB.get_user_info(user_id))
        haracteristics = await user_info.get_aviable_haracteristics()
        max_hp = haracteristics[0]

        proc_dict = {
            25: max_hp / 4,
            50: max_hp / 2,
            75: max_hp / 4 * 3,
            100: max_hp
        }
        return round(proc_dict.get(self.up_hp_proc)) if self.up_hp_proc else 0

    async def get_potion_result(self, user_id):
        res_message = []
        for eff in self.effects:
            if self.effects[eff]:
                if eff == "current_hp":
                    res_message.append(f"{strings.potion_res_info[eff]} +{await self.get_proc_heal(user_id)}")
                else:
                    res_message.append(f"{strings.potion_res_info[eff]} +{self.effects[eff]}%")

        return f"{strings.potion_been_used}\n\n" + '\n'.join(res_message)
