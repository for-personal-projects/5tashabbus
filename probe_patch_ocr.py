p = r"d:\5tashabbus_bot\bot.py"
s = open(p, encoding="utf-8").read()  # text-mode: CRLF -> LF
orig = s

# 1) import qoshish
a = "from image_utils import compress_image\n"
assert a in s, "import anchor topilmadi"
s = s.replace(a, a + "import captcha_ocr\n", 1)

# 2) send_captcha: OCR + tasdiqlash tugmasi
old_block = (
    "    await state.update_data(request_id=rid)\n"
    "    await msg.answer_photo(BufferedInputFile(img, \"captcha.png\"),\n"
    "        caption=texts.ASK_CAPTCHA, reply_markup=kb.captcha_kb(), parse_mode=\"HTML\")\n"
)
assert old_block in s, "send_captcha blok topilmadi"
new_block = (
    "    auto = await loop.run_in_executor(None, captcha_ocr.read_captcha, img)\n"
    "    await state.update_data(request_id=rid, auto_code=auto)\n"
    "    caption = texts.ASK_CAPTCHA\n"
    "    if auto:\n"
    "        caption += (\"\\n\\n\U0001F916 <b>Aniqlangan captcha: <code>%s</code></b>\\n\"\n"
    "                    \"Tizim captchani avtomatik aniqladi, tasdiqlaysizmi?\" % auto)\n"
    "    await msg.answer_photo(BufferedInputFile(img, \"captcha.png\"),\n"
    "        caption=caption, reply_markup=kb.captcha_kb(auto=bool(auto)), parse_mode=\"HTML\")\n"
)
s = s.replace(old_block, new_block, 1)

# 3) m_captcha: kichik harf -> KATTA
old_mc = '    raw = (msg.text or "").strip()\n    code = raw.upper()'
assert old_mc in s, "m_captcha normalize joyi topilmadi"
s = s.replace(old_mc,
    '    raw = (msg.text or "").strip().upper()\n    code = raw', 1)

# write: text-mode LF -> CRLF (Windows)
open(p, "w", encoding="utf-8").write(s)
print("PATCHED:", len(orig), "->", len(s))
