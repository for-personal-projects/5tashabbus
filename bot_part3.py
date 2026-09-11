@dp.callback_query(F.data.startswith("obl:"))
async def cb_oblast(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data.startswith("obl:page:"):
        page = int(call.data.split(":")[-1])
        return await call.message.edit_reply_markup(
            reply_markup=kb.list_kb("obl", data.get("oblasts", []), page))
    oid = int(call.data.split(":")[1])
    api = api_of(call.from_user.id)
    loop = asyncio.get_event_loop()
    try:
        regions = await loop.run_in_executor(None, lambda: api.get_regions(oid))
    except Exception as e:
        return await call.answer(f"Xato: {e}", show_alert=True)
    names = {x["id"]: x["name"] for x in data.get("oblasts", [])}
    await state.update_data(oblast_id=oid, oblast_name=names.get(oid, str(oid)), regions=regions)
    await state.set_state(Reg.region)
    await call.message.answer(texts.ASK_REGION, reply_markup=kb.list_kb("reg", regions))
    await call.answer()


@dp.callback_query(F.data.startswith("reg:"))
async def cb_region(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data.startswith("reg:page:"):
        page = int(call.data.split(":")[-1])
        return await call.message.edit_reply_markup(
            reply_markup=kb.list_kb("reg", data.get("regions", []), page))
    rid = int(call.data.split(":")[1])
    api = api_of(call.from_user.id)
    loop = asyncio.get_event_loop()
    try:
        mfy = await loop.run_in_executor(None, lambda: api.get_mfy(rid))
    except Exception as e:
        return await call.answer(f"Xato: {e}", show_alert=True)
    names = {x["id"]: x["name"] for x in data.get("regions", [])}
    await state.update_data(region_id=rid, region_name=names.get(rid, str(rid)), mfy_list=mfy)
    await state.set_state(Reg.mfy)
    await call.message.answer(texts.ASK_MFY, reply_markup=kb.list_kb("mfy", mfy, label="name", vid="id"))
    await call.answer()


@dp.callback_query(F.data.startswith("mfy:"))
async def cb_mfy(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data.startswith("mfy:page:"):
        page = int(call.data.split(":")[-1])
        return await call.message.edit_reply_markup(
            reply_markup=kb.list_kb("mfy", data.get("mfy_list", []), page))
    mid = int(call.data.split(":")[1])
    names = {x["id"]: x["name"] for x in data.get("mfy_list", [])}
    await state.update_data(mfy_id=mid, mfy_name=names.get(mid, str(mid)))
    # sport kategoriyalar
    api = api_of(call.from_user.id)
    loop = asyncio.get_event_loop()
    athlete = data.get("athlete", {})
    await call.message.answer("⏳ Sport yo'nalishlari yuklanmoqda...")
    try:
        scode, scats = await loop.run_in_executor(None,
            lambda: api.get_sport_categories(athlete.get("genderid", 1), data["initiativ_id"]))
    except Exception as e:
        return await call.message.answer(f"Sport kategoriya yuklanmadi: {e}")
    if scode != 200 or not isinstance(scats, list):
        return await call.message.answer(f"Sport kategoriya xato ({scode}): {str(scats)[:500]}")
    await state.update_data(sportcats=scats)
    await state.set_state(Reg.sportcat)
    await call.message.answer(texts.ASK_SPORTCAT, reply_markup=kb.list_kb("scat", scats))
    await call.answer()
