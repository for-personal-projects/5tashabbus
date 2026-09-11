p = r"d:\5tashabbus_bot\keyboards.py"
s = open(p, encoding="utf-8").read()

old_kb = (
    "def captcha_kb():\n"
    "    return InlineKeyboardMarkup(inline_keyboard=[[\n"
    "        InlineKeyboardButton(text=\"\U0001F504 Yangi rasm\", callback_data=\"captcha:refresh\")]])\n"
)
assert old_kb in s, "captcha_kb topilmadi"

new_kb = (
    "def captcha_kb(auto: str | None = None):\n"
    "    \"\"\"auto berilsa — avtomatik aniqlangan captchani tasdiqlash tugmasi ham chiqadi.\"\"\"\n"
    "    rows = []\n"
    "    if auto:\n"
    "        rows.append([InlineKeyboardButton(\n"
    "            text=f\"\u2705 Ha, tasdiqlayman ({auto})\",\n"
    "            callback_data=\"captcha:use_auto\")])\n"
    "    rows.append([InlineKeyboardButton(text=\"\U0001F504 Yangi rasm\",\n"
    "                                      callback_data=\"captcha:refresh\")])\n"
    "    return InlineKeyboardMarkup(inline_keyboard=rows)\n"
)
s = s.replace(old_kb, new_kb, 1)
open(p, "w", encoding="utf-8").write(s)
print("KB-PATCHED")
