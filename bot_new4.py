@dp.callback_query(F.data.startswith("init:"))
async def cb_init(call: CallbackQuery, state: FSMContext):
    await state.update_data(initiativ_id=int(call.data.split(":")[1]))
    await state.set_state(Reg.identity)
    await call.message.answer(texts.ASK_IDOC, reply_markup=kb.identity_kb())
    await call.answer()


@dp.callback_query(F.data.startswith("idoc:"))
async def cb_idoc(call: CallbackQuery, state: FSMContext):
    await state.update_data(identity_id=int(call.data.split(":")[1]))
    await state.set_state(Reg.series)
    await call.message.answer(texts.ASK_SERIES, parse_mode="HTML")
    await call.answer()


@dp.message(Reg.series)
async def m_series(msg: Message, state: FSMContext):
    v = (msg.text or "").strip().upper()
    if len(v) < 3:
        return await msg.answer("Seriya juda qisqa. Masalan: I-HR")
    await state.update_data(series=v)
    await state.set_state(Reg.number)
    await msg.answer(texts.ASK_NUMBER, parse_mode="HTML")


@dp.message(Reg.number)
async def m_number(msg: Message, state: FSMContext):
    v = (msg.text or "").strip()
    if not re.match(r"^[0-9]{5,10}$", v):
        return await msg.answer("Raqam faqat raqamlardan iborat bo'lsin (5-10 ta).")
    await state.update_data(number=v)
    await state.set_state(Reg.dob)
    await msg.answer(texts.ASK_DOB, parse_mode="HTML")


@dp.message(Reg.dob)
async def m_dob(msg: Message, state: FSMContext):
    v = (msg.text or "").strip()
    if not valid_dob(v):
        return await msg.answer("Format noto'g'ri. Namuna: 22.06.2014")
    await state.update_data(dob=v)
    await state.set_state(Reg.captcha)
    await send_captcha(msg, state)


@dp.callback_query(F.data == "captcha:refresh")
async def cb_captcha_refresh(call: CallbackQuery, state: FSMContext):
    cur = await state.get_state()
    if cur != Reg.captcha.state:
        return await call.answer("Hozir captcha kerak emas", show_alert=True)
    await send_captcha(call.message, state)
    await call.answer("Yangi rasm")


@dp.message(Reg.captcha)
async def m_captcha(msg: Message, state: FSMContext):
    data = await state.get_data()
    code = ((msg.text or "").strip().upper())
    if not re.match(r"^[A-Z0-9]{3,6}$", code):
        return await msg.answer("Captcha 4 ta harf/raqam. Qayta kiriting yoki 🔄 bosing.")
    api = api_of(msg.from_user.id)
    # captcha id siga profil telefonini ham bog'laymiz (sayt phoneNumber bilan generatsiya qiladi)
    loop = asyncio.get_event_loop()
    wait = await msg.answer("⏳ Tekshirilmoqda...")
    try:
        status, body = await loop.run_in_executor(None, lambda: api.get_athlete_info(
            data["series"], data["number"], data["dob"],
            data["identity_id"], data["initiativ_id"], code))
    except Exception as e:
        return await wait.edit_text(f"🌐 API ga ulanib bo'lmadi (sayt sekin/tirik emas): {e}")
    if status == 200 and isinstance(body, dict) and body.get("result"):
        res = body["result"]
        await state.update_data(athlete=res)
        await wait.delete()
        await msg.answer(fmt_athlete(res))
        await state.set_state(Reg.found)
        try:
            oblasts = await loop.run_in_executor(None, api.get_oblasts)
            await state.update_data(oblasts=oblasts)
            await state.set_state(Reg.oblast)
            await msg.answer(texts.ASK_OBLAST, reply_markup=kb.list_kb("obl", oblasts))
        except Exception as e:
            await msg.answer(f"Topildi, lekin viloyat ro'yxatini olib bo'lmadi: {e}\n"
                "Qayta boshlash: /start")
        return
    err = body.get("error", body) if isinstance(body, dict) else str(body)
    new_b64 = body.get("captcha") if isinstance(body, dict) else None
    txt = f"{texts.CAPTCHA_FAIL}\n\n<b>Server:</b> <code>{html.escape(str(err))}</code>{texts.API_400_HINT}"
    if new_b64:
        try:
            img = base64.b64decode(new_b64)
            await wait.delete()
            await msg.answer_photo(BufferedInputFile(img, "captcha.png"),
                caption=txt, reply_markup=kb.captcha_kb(), parse_mode="HTML")
            return
        except Exception:
            pass
    await wait.delete()
    await msg.answer(txt, parse_mode="HTML")
    await send_captcha(msg, state)
