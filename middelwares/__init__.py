from aiogram import Dispatcher

from .LastActionMiddelware import TimeLastActionMiddelware
from .ThrottlingMiddleware import ThrottlingMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(TimeLastActionMiddelware())
