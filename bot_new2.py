async def send_captcha(msg: Message, state: FSMContext):
    api = api_of(msg.from_user.id)
    loop = asyncio.get_event_loop()
    rid, img = await loop.run_in_executor(None, api.new_captcha)
    await state.update_data(request_id=rid)
    await msg.answer_photo(BufferedInputFile(img, "captcha.png"),
        caption=texts.ASK_CAPTCHA, reply_markup=kb.captcha_kb(), parse_mode="HTML")


async def start_flow(msg: Message, state: FSMContext):
    """1-qadamdan boshlash: telefon so'rash."""
    await state.clear()
    user_api[msg.from_user.id] = TashabbusApi()
    await state.set_state(Reg.phone)
    await msg.answer(texts.START, parse_mode="HTML")
    await msg.answer(texts.ASK_PHONE_FIRST, parse_mode="HTML",
                     reply_markup=kb.phone_kb())


@dp.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await start_flow(msg, state)


@dp.message(Command("register"))
async def cmd_register(msg: Message, state: FSMContext):
    await start_flow(msg, state)


@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(texts.HELP)


@dp.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(texts.CANCELLED, reply_markup=kb.remove_kb())
