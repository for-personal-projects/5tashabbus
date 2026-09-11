"""Telegram bot — 5tashabbus ro'yxatdan o'tkazish (aiogram 3.x)."""
import asyncio
import base64
import io
import logging
import re

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (BufferedInputFile, CallbackQuery, Message)

import config
import texts
import keyboards as kb
from states import Reg
from tashabbus_api import TashabbusApi, fmt_athlete, log

dp = Dispatcher(storage=MemoryStorage())
user_api: dict[int, TashabbusApi] = {}


def api_of(uid: int) -> TashabbusApi:
    if uid not in user_api:
        user_api[uid] = TashabbusApi()
    return user_api[uid]


def valid_dob(s: str) -> bool:
    return bool(re.match(r"^\d{2}\.\d{2}\.\d{4}$", s.strip()))


async def send_captcha(msg: Message, state: FSMContext):
    api = api_of(msg.from_user.id)
    loop = asyncio.get_event_loop()
    rid, img = await loop.run_in_executor(None, api.new_captcha)
    await state.update_data(request_id=rid)
    await msg.answer_photo(BufferedInputFile(img, "captcha.png"),
        caption=texts.ASK_CAPTCHA, reply_markup=kb.captcha_kb(), parse_mode="HTML")
