@dp.message(Reg.phone)
async def m_phone(msg: Message, state: FSMContext):
    v = re.sub(r"[\s\-()]", "", msg.text.strip())
    if not re.match(r"^\+?998\d{9}$", v):
        if v.startswith("9") and len(v) == 9:
            v = "+998" + v
        else:
            return await msg.answer("Noto'g'ri. Namuna: +998901234567")
    if not v.startswith("+"):
        v = "+" + v
    await state.update_data(phone=v)
    await state.set_state(Reg.photo)
    await msg.answer(texts.ASK_PHOTO)


@dp.message(Reg.photo, F.photo)
async def m_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    api = api_of(msg.from_user.id)
    bot: Bot = msg.bot
    ph = msg.photo[-1]
    f = await bot.get_file(ph.file_id)
    buf = io.BytesIO()
    await bot.download_file(f.file_path, buf)
    img = buf.getvalue()
    if len(img) > 200*1024:
        await msg.answer(f"⚠️ Rasm {len(img)//1024}KB — sayt 200KB talab qiladi, baribir yuborib ko'ramiz.")
    loop = asyncio.get_event_loop()
    wait = await msg.answer("⏳ Rasm yuklanmoqda...")
    try:
        scode, body = await loop.run_in_executor(None, lambda: api.attach_photo(img, "photo.jpg"))
    except Exception as e:
        return await wait.edit_text(f"Rasm yuklanmadi: {e}")
    if scode != 200 or not isinstance(body, dict) or not body.get("id"):
        await wait.delete()
        await state.update_data(photo_file_id="")
        await msg.answer(f"Rasm serverga yuklanmadi ({scode}): {str(body)[:500]}\nDavom etamiz.")
    else:
        await wait.delete()
        await state.update_data(photo_file_id=body["id"], photo_info=body)
        await msg.answer(f"📷 Rasm qabul qilindi (id={body['id']}).")
    d2 = await state.get_data()
    athlete = d2.get("athlete", {})
    await state.set_state(Reg.confirm)
    await msg.answer(texts.CONFIRM_TMPL.format(
        athlete=fmt_athlete(athlete), init=config.INITIATIV_TYPES.get(d2.get("initiativ_id"), "?"),
        oblast=d2.get("oblast_name", "?"), region=d2.get("region_name", "?"),
        mfy=d2.get("mfy_name", "?"), sport=d2.get("sport_names", "?"),
        phone=d2.get("phone", "?")), parse_mode="HTML", reply_markup=kb.confirm_kb())


@dp.message(Reg.photo)
async def m_photo_wrong(msg: Message):
    await msg.answer("Rasm yuboring (galereyadan foto sifatida, fayl emas).")


@dp.callback_query(F.data.startswith("confirm:"))
async def cb_confirm(call: CallbackQuery, state: FSMContext):
    if call.data == "confirm:no":
        await state.clear()
        return await call.message.answer(texts.CANCELLED)
    data = await state.get_data()
    athlete = data.get("athlete", {})
    applicant = dict(athlete)
    applicant.update({
        "oblastid": data.get("oblast_id"), "regionid": data.get("region_id"),
        "mfyid": data.get("mfy_id"), "initiativtypeid": data.get("initiativ_id"),
        "sporttypecategoryid": data.get("sportcat_id"),
        "sporttypeids": data.get("sport_ids", []),
        "agecategoryid": data.get("agecat_id") or None,
        "phonenumber": data.get("phone", ""), "mobilenumber": data.get("phone", ""),
        "identitydocumentid": data.get("identity_id"),
        "photo": {"id": 0, "ownerid": 0,
                  "attachmentfileid": data.get("photo_file_id", ""),
                  "attachmentfilename": "", "attachmentfiletype": "",
                  "isphoto": True, "statusid": 0, "Status": 1},
    })
    api = api_of(call.from_user.id)
    loop = asyncio.get_event_loop()
    await call.message.answer("⏳ Yuborilmoqda...")
    try:
        scode, body = await loop.run_in_executor(None, lambda: api.insert_registration(applicant))
    except Exception as e:
        return await call.message.answer(f"🌐 Yuborilmadi: {e}")
    if scode in (200, 201) and (not isinstance(body, dict) or body.get("success", True)):
        await state.clear()
        await call.message.answer(texts.SENT_OK)
    else:
        await call.message.answer(texts.SENT_FAIL.format(err=str(body)[:1500]))
    await call.answer()


async def main():
    if not config.BOT_TOKEN:
        print("BOT_TOKEN topilmadi. .env ga BOT_TOKEN=... qo'shing. Namuna: .env.example")
        raise SystemExit(1)
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
