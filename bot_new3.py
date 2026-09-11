@dp.message(Command("status"))
async def cmd_status(msg: Message):
    rows = await store.list_registrations(msg.from_user.id)
    if not rows:
        return await msg.answer(texts.STATUS_EMPTY)
    phone = rows[-1].get("phone", "") or user_phone.get(msg.from_user.id, "")
    head = texts.STATUS_HEAD.format(n=len(rows), phone=html.escape(phone or "—"))
    lines = []
    for i, r in enumerate(rows, 1):
        nm = html.escape(r.get("fullname", "?") or "?")
        doc = html.escape(f"{r.get('series','')} {r.get('number','')}".strip())
        dob = html.escape(r.get("dob", "") or "")
        ini = html.escape(r.get("initiativ", "") or "")
        sp = html.escape(r.get("sport", "") or "")
        dt = html.escape(r.get("created_at", "") or "")
        extra = " • ".join(x for x in [doc, dob, ini, sp] if x)
        lines.append(f"{i}. <b>{nm}</b>" + (f" — {extra}" if extra else "") + f" <i>({dt})</i>")
    # 4096 chegaradan oshsa bo'laklab yuborish
    chunks, cur = [], head
    for ln in lines:
        if len(cur) + len(ln) + 1 > 3900:
            chunks.append(cur)
            cur = ""
        cur += ln + "\n"
    if cur.strip():
        chunks.append(cur)
    for c in chunks:
        await msg.answer(c, parse_mode="HTML")


@dp.message(Reg.phone, F.contact)
async def m_phone_contact(msg: Message, state: FSMContext):
    v = norm_phone(msg.contact.phone_number)
    if not v:
        return await msg.answer("Raqamni aniqlab bo'lmadi. Qo'lda yozing: +998901234567")
    user_phone[msg.from_user.id] = v
    await state.update_data(phone=v)
    await state.set_state(Reg.initiativ)
    await msg.answer(f"✅ Profil: <code>{html.escape(v)}</code>\nBolalar shu profildan yuklanadi.",
                     parse_mode="HTML", reply_markup=kb.remove_kb())
    await msg.answer(texts.ASK_INIT, reply_markup=kb.initiativ_kb())


@dp.message(Reg.phone)
async def m_phone_text(msg: Message, state: FSMContext):
    v = norm_phone(msg.text or "")
    if not v:
        return await msg.answer("Noto'g'ri. Namuna: <code>+998901234567</code> "
            "yoki pastdagi tugma bilan yuboring.", parse_mode="HTML")
    user_phone[msg.from_user.id] = v
    await state.update_data(phone=v)
    await state.set_state(Reg.initiativ)
    await msg.answer(f"✅ Profil: <code>{html.escape(v)}</code>\nBolalar shu profildan yuklanadi.",
                     parse_mode="HTML", reply_markup=kb.remove_kb())
    await msg.answer(texts.ASK_INIT, reply_markup=kb.initiativ_kb())
