@dp.callback_query(F.data.startswith("scat:"))
async def cb_scat(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data.startswith("scat:page:"):
        page = int(call.data.split(":")[-1])
        return await call.message.edit_reply_markup(
            reply_markup=kb.list_kb("scat", data.get("sportcats", []), page))
    scid = int(call.data.split(":")[1])
    await state.update_data(sportcat_id=scid)
    api = api_of(call.from_user.id)
    loop = asyncio.get_event_loop()
    athlete = data.get("athlete", {})
    try:
        scode, sports = await loop.run_in_executor(None, lambda: api.get_sport_types(
            athlete.get("genderid", 1), data["initiativ_id"],
            athlete.get("dateofbirth", ""), 0, scid))
    except Exception as e:
        return await call.message.answer(f"Sport turlari yuklanmadi: {e}")
    if scode != 200 or not isinstance(sports, list):
        return await call.message.answer(f"Sport turlari xato ({scode}): {str(sports)[:800]}")
    await state.update_data(sports=sports)
    names = "\n".join(f"{i+1}. {s.get('name')} (id={s.get('id')})" for i, s in enumerate(sports[:40]))
    await state.set_state(Reg.sport)
    await call.message.answer(f"{texts.ASK_SPORT}\n\n{names}")
    await call.answer()


@dp.message(Reg.sport)
async def m_sport(msg: Message, state: FSMContext):
    data = await state.get_data()
    sports = data.get("sports", [])
    by_idx = {str(i+1): s for i, s in enumerate(sports)}
    by_id = {str(s.get("id")): s for s in sports}
    picks = []
    for tok in msg.text.replace(",", " ").split():
        s = by_idx.get(tok.strip()) or by_id.get(tok.strip())
        if s:
            picks.append(s)
    if not picks:
        return await msg.answer("Topilmadi. Ro'yxatdagi raqam yoki id ni yuboring.")
    await state.update_data(sport_ids=[p["id"] for p in picks],
        sport_names=", ".join(p.get("name", "?") for p in picks))
    api = api_of(msg.from_user.id)
    loop = asyncio.get_event_loop()
    athlete = data.get("athlete", {})
    try:
        acode, acats = await loop.run_in_executor(None, lambda: api.get_age_categories(
            athlete.get("genderid", 1), athlete.get("dateofbirth", ""), data["initiativ_id"]))
    except Exception as e:
        return await msg.answer(f"Yosh kategoriya yuklanmadi: {e}")
    if acode != 200 or not isinstance(acats, list) or not acats:
        await state.set_state(Reg.phone)
        return await msg.answer(
            f"Tanlandi: {', '.join(p.get('name','?') for p in picks)}\n\n" + texts.ASK_PHONE,
            parse_mode="HTML")
    await state.update_data(agecats=acats)
    await state.set_state(Reg.agecat)
    await msg.answer(texts.ASK_AGECAT, reply_markup=kb.list_kb("age", acats))


@dp.callback_query(F.data.startswith("age:"))
async def cb_age(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data.startswith("age:page:"):
        page = int(call.data.split(":")[-1])
        return await call.message.edit_reply_markup(
            reply_markup=kb.list_kb("age", data.get("agecats", []), page))
    await state.update_data(agecat_id=int(call.data.split(":")[1]))
    await state.set_state(Reg.phone)
    await call.message.answer(texts.ASK_PHONE, parse_mode="HTML")
    await call.answer()
