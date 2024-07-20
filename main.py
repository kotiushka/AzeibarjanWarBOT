import asyncio
import logging

from utils.functions import clear_quests, schedule

logging.basicConfig(level=logging.INFO)


async def on_startup(dp):
    import middelwares
    from database import DB


    await DB.set_clan_war_next_war()
    asyncio.create_task(schedule())
    asyncio.create_task(clear_quests(2*60*60))
    middelwares.setup(dp)



if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
