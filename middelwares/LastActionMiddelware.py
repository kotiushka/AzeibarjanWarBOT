from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from AzeibarjanWarBOT.database import DB


class TimeLastActionMiddelware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if await DB.user_check(message.from_user.id):
            await DB.update_last_action(round(message.date.timestamp()), message.from_user.id)


