"""Telegram bot — 5tashabbus ro'yxatdan o'tkazish (aiogram 3.x).

Yangi tartib (foydalanuvchi aytgani bo'yicha):
  /start -> 1) telefon (profil; bolalar shu profildan yuklanadi)
         -> 2) yo'nalish -> 3) hujjat turi -> 4) seriya -> 5) raqam
         -> 6) tug'ilgan sana -> 7) captcha -> qidirish -> qolgan qadamlar
         -> yuborilgach sqlite ga saqlanadi; /status soni+ismlarni chiqaradi.
"""
import asyncio
import base64
import html
import io
import logging
import re

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BufferedInputFile, CallbackQuery, Message

import config
import texts
import keyboards as kb
import store
from states import Reg
from tashabbus_api import TashabbusApi, fmt_athlete, log

dp = Dispatcher(storage=MemoryStorage())
user_api: dict[int, TashabbusApi] = {}
user_phone: dict[int, str] = {}


def api_of(uid: int) -> TashabbusApi:
    if uid not in user_api:
        user_api[uid] = TashabbusApi()
    return user_api[uid]


def valid_dob(s: str) -> bool:
    return bool(re.match(r"^\d{2}\.\d{2}\.\d{4}$", s.strip()))


def norm_phone(raw: str):
    v = re.sub(r"[\s\-()]", "", (raw or "").strip())
    if re.match(r"^\+?998\d{9}$", v):
        return "+" + v.lstrip("+")
    if re.match(r"^9\d{8}$", v):
        return "+998" + v
    if re.match(r"^8\d{9}$", v):
        return "+998" + v[1:]
    return None
