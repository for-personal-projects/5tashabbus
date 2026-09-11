"""Klaviaturalar: saytdagi tanlovlar aynani."""
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton)


def phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True)


def remove_kb():
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()


def initiativ_kb(online_only=True):
    import config
    rows = []
    for i, name in config.INITIATIV_TYPES.items():
        if online_only and i not in (2, 3):
            continue
        rows.append([InlineKeyboardButton(text=name, callback_data=f"init:{i}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def identity_kb():
    import config
    rows = [[InlineKeyboardButton(text=v, callback_data=f"idoc:{k}")]
            for k, v in config.IDENTITY_DOCS.items()]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def captcha_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔄 Yangi rasm", callback_data="captcha:refresh")]])


def list_kb(prefix: str, items: list, page: int = 0, per: int = 8,
            label="name", vid="id"):
    chunk = items[page*per:(page+1)*per]
    rows = [[InlineKeyboardButton(text=str(x.get(label, "?"))[:50],
                                  callback_data=f"{prefix}:{x.get(vid)}")] for x in chunk]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}:page:{page-1}"))
    if (page+1)*per < len(items):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}:page:{page+1}"))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm:yes")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="confirm:no")],
    ])


def more_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yana bola qo'shish", callback_data="more:yes")],
        [InlineKeyboardButton(text="📊 Ro'yxatim (/status)", callback_data="more:status")],
    ])
