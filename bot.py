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
import exporter
import debuglog
from debuglog import save_captcha
from image_utils import compress_image
import captcha_ocr
from states import Reg
from tashabbus_api import TashabbusApi, fmt_athlete, log as api_log

dp = Dispatcher(storage=MemoryStorage())
user_api: dict[int, TashabbusApi] = {}
user_phone: dict[int, str] = {}
log = logging.getLogger("bot")


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

async def send_captcha(msg: Message, state: FSMContext):
    uid = msg.from_user.id
    api = api_of(uid)
    phone = user_phone.get(uid) or (await state.get_data()).get("phone")
    log.info("STEP captcha: uid=%s phone=%r -> yangi captcha olinmoqda", uid, phone)
    loop = asyncio.get_event_loop()
    rid, img, used_phone = await loop.run_in_executor(None, lambda: api.new_captcha(phone))
    save_captcha(uid, img, "gen")
    auto = await loop.run_in_executor(None, captcha_ocr.read_captcha, img)
    await state.update_data(request_id=rid, auto_code=auto)
    caption = texts.ASK_CAPTCHA
    if auto:
        caption += ("\n\n🤖 <b>Aniqlangan captcha: <code>%s</code></b>\n"
                    "Tizim captchani avtomatik aniqladi, tasdiqlaysizmi?" % auto)
    await msg.answer_photo(BufferedInputFile(img, "captcha.png"),
        caption=caption, reply_markup=kb.captcha_kb(auto=bool(auto)), parse_mode="HTML")


async def start_flow(uid: int, dest: Message, state: FSMContext):
    """1-qadamdan boshlash: telefon so'rash. Eski jarayon tozalanadi (state.clear)."""
    await state.clear()
    user_api[uid] = TashabbusApi()
    await state.set_state(Reg.phone)
    await dest.answer(texts.START, parse_mode="HTML")
    await dest.answer(texts.ASK_PHONE_FIRST, parse_mode="HTML",
                     reply_markup=kb.phone_kb())


@dp.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await start_flow(msg.from_user.id, msg, state)


@dp.message(Command("register"))
async def cmd_register(msg: Message, state: FSMContext):
    await start_flow(msg.from_user.id, msg, state)


@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(texts.HELP)


@dp.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    log.info("STEP cancel: uid=%s — jarayon tozalanadi", msg.from_user.id)
    await state.clear()
    await msg.answer(texts.CANCELLED, reply_markup=kb.remove_kb())


@dp.message(Command("diag"))
async def cmd_diag(msg: Message, state: FSMContext):
    """Faqat admin: captcha rostdan ishlayaptimi yoki ma'lumotda muammo bor — tekshirish."""
    if msg.from_user.id not in config.ADMIN_IDS:
        return
    uid = msg.from_user.id
    log.info("DIAG: admin %s diag boshladi", uid)
    api = api_of(uid)
    loop = asyncio.get_event_loop()
    rid, img, used_phone = await loop.run_in_executor(None, lambda: api.new_captcha())
    save_captcha(uid, img, "diag_gen")
    await state.set_state(Reg.diag_captcha)
    await state.update_data(request_id=rid)
    await msg.answer_photo(
        BufferedInputFile(img, "diag_captcha.png"),
        caption=("🔬 <b>Diagnostika:</b> rasmdeki 4 ta belgini yuboring.\n"
                 "Bot uni <b>soxta hujjat</b> bilan tekshiradi.\n"
                 "• Agar <code>Captcha mos kelmadi</code> kelsa → captcha bog'lanishida muammo\n"
                 "• Agar boshqa xato (masalan «topilmadi») kelsa → captcha OK, muammo ma'lumotda"),
        parse_mode="HTML")


@dp.message(Reg.diag_captcha)
async def m_diag(msg: Message, state: FSMContext):
    uid = msg.from_user.id
    if uid not in config.ADMIN_IDS:
        return await msg.answer("Faqat admin uchun.")
    code = (msg.text or "").strip().upper()
    api = api_of(uid)
    loop = asyncio.get_event_loop()
    wait = await msg.answer("⏳ Diagnostika so'rovi yuborilmoqda...")
    log.info("DIAG: uid=%s code=%r guid=%s", uid, code, api.request_id)
    try:
        status, body = await loop.run_in_executor(None, lambda: api.get_athlete_info(
            "XX", "0000000", "01.01.1990", 1, 2, code))
    except Exception as e:
        log.exception("DIAG: API xato uid=%s: %s", uid, e)
        return await wait.edit_text(f"API xato: {e}")
    err = body.get("error") if isinstance(body, dict) else str(body)
    verdict = (
        "🔬 <b>Diagnostika natijasi:</b>\n"
        f"HTTP: <code>{status}</code>\n"
        f"Server xabari: <code>{html.escape(str(err))}</code>\n\n")
    if isinstance(body, dict) and "Captcha" in str(err):
        verdict += ("❌ <b>Captcha rostdan mos kelmadi.</b>\n"
            "Rasmni qayta ochib yozgan kodingizni solishtiring "
            "(0/O, 1/I/L, 5/S, 2/Z chalkashadi). Har xatoda bot yangi rasm yuboradi.")
    elif status == 200 or (isinstance(body, dict) and body.get("result")):
        verdict += "⚠️ Soxta ma'lumot bilan ham natija qaytdi — captcha OK, lekin tekshirish kerak."
    else:
        verdict += ("✅ <b>Captcha ISHLAYDI!</b> («topilmadi» kabi boshqa xato keldi)\n"
            "Demak oldingi «Captcha mos kelmadi» xatolari shu sabab bo'lgan bo'lishi mumkin:\n"
            "• rasmdagi belgilarni boshqa o'qigan (0↔O, 1↔I/L, 5↔S, 2↔Z)\n"
            "• yoki o'sha payt eski guid ishlatilgan — endi har xatoda yangi guid oladi.")
    log.info("DIAG: uid=%s natija status=%s err=%r", uid, status, err)
    await wait.edit_text(verdict, parse_mode="HTML")
    await state.set_state(Reg.captcha)
    await send_captcha(msg, state)

async def status_for(uid: int, dest: Message):
    rows = await store.list_registrations(uid)
    if not rows:
        return await dest.answer(texts.STATUS_EMPTY)
    phone = rows[-1].get("phone", "") or user_phone.get(uid, "")
    head = texts.STATUS_HEAD.format(n=len(rows))
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
        await dest.answer(c, parse_mode="HTML")


@dp.message(Command("status"))
async def cmd_status(msg: Message):
    await status_for(msg.from_user.id, msg)


async def send_excel(uid: int, dest: Message):
    rows = await store.list_registrations(uid)
    if not rows:
        return await dest.answer(texts.EXPORT_EMPTY)
    data = await asyncio.get_event_loop().run_in_executor(None, exporter.build_excel, rows)
    from datetime import datetime
    fname = f"royxat_{datetime.now():%Y-%m-%d}.xlsx"
    await dest.answer_document(
        BufferedInputFile(data, filename=fname),
        caption=texts.EXPORT_SENT.format(n=len(rows)))


@dp.message(Command("export", "excel"))
async def cmd_export(msg: Message):
    await send_excel(msg.from_user.id, msg)


@dp.message(Reg.phone, F.contact)
async def m_phone_contact(msg: Message, state: FSMContext):
    v = norm_phone(msg.contact.phone_number)
    log.info("STEP phone: uid=%s contact=%r -> normalized=%r",
             msg.from_user.id, msg.contact.phone_number, v)
    if not v:
        return await msg.answer("Raqamni aniqlab bo'lmadi. Qayta yuboring.")
    user_phone[msg.from_user.id] = v
    await state.update_data(phone=v)
    await state.set_state(Reg.initiativ)
    await msg.answer(f"✅ Profil: <code>{html.escape(v)}</code>",
                     parse_mode="HTML", reply_markup=kb.remove_kb())
    await msg.answer(texts.ASK_INIT, reply_markup=kb.initiativ_kb())


@dp.message(Reg.phone)
async def m_phone_text(msg: Message, state: FSMContext):
    v = norm_phone(msg.text or "")
    log.info("STEP phone: uid=%s text=%r -> normalized=%r", msg.from_user.id, msg.text, v)
    if not v:
        return await msg.answer("Noto'g'ri raqam. Masalan: <code>+998901234567</code>",
                                parse_mode="HTML")
    user_phone[msg.from_user.id] = v
    await state.update_data(phone=v)
    await state.set_state(Reg.initiativ)
    await msg.answer(f"✅ Profil: <code>{html.escape(v)}</code>",
                     parse_mode="HTML", reply_markup=kb.remove_kb())
    await msg.answer(texts.ASK_INIT, reply_markup=kb.initiativ_kb())

@dp.callback_query(F.data.startswith("init:"))
async def cb_init(call: CallbackQuery, state: FSMContext):
    log.info("STEP initiativ: uid=%s -> %s", call.from_user.id, call.data)
    await state.update_data(initiativ_id=int(call.data.split(":")[1]))
    await state.set_state(Reg.identity)
    await call.message.answer(texts.ASK_IDOC, reply_markup=kb.identity_kb())
    await call.answer()


@dp.callback_query(F.data.startswith("idoc:"))
async def cb_idoc(call: CallbackQuery, state: FSMContext):
    log.info("STEP identity: uid=%s -> %s", call.from_user.id, call.data)
    await state.update_data(identity_id=int(call.data.split(":")[1]))
    await state.set_state(Reg.series)
    await call.message.answer(texts.ASK_SERIES, parse_mode="HTML")
    await call.answer()


@dp.message(Reg.series)
async def m_series(msg: Message, state: FSMContext):
    v = (msg.text or "").strip().upper()
    log.info("STEP series: uid=%s -> %r", msg.from_user.id, v)
    if len(v) < 3:
        return await msg.answer("Seriya juda qisqa. Masalan: I-HR")
    await state.update_data(series=v)
    await state.set_state(Reg.number)
    await msg.answer(texts.ASK_NUMBER, parse_mode="HTML")


@dp.message(Reg.number)
async def m_number(msg: Message, state: FSMContext):
    v = (msg.text or "").strip()
    log.info("STEP number: uid=%s -> %r", msg.from_user.id, v)
    if not re.match(r"^[0-9]{5,10}$", v):
        return await msg.answer("Raqam faqat raqamlardan iborat bo'lsin (5-10 ta).")
    await state.update_data(number=v)
    await state.set_state(Reg.dob)
    await msg.answer(texts.ASK_DOB, parse_mode="HTML")


@dp.message(Reg.dob)
async def m_dob(msg: Message, state: FSMContext):
    v = (msg.text or "").strip()
    log.info("STEP dob: uid=%s -> %r", msg.from_user.id, v)
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
    uid = msg.from_user.id
    data = await state.get_data()
    raw = (msg.text or "").strip().upper()
    code = raw
    log.info("STEP captcha: uid=%s kiritildi raw=%r upper=%r len=%s guid=%s",
             uid, raw, code, len(raw), data.get("request_id"))
    if not re.match(r"^[A-Z0-9]{3,6}$", code):
        log.warning("STEP captcha: uid=%s noto'g'ri format: %r", uid, raw)
        return await msg.answer("Captcha 4 ta harf/raqam. Qayta kiriting yoki 🔄 bosing.")
    api = api_of(uid)
    loop = asyncio.get_event_loop()
    wait = await msg.answer("⏳ Tekshirilmoqda...")
    try:
        status, body = await loop.run_in_executor(None, lambda: api.get_athlete_info(
            data["series"], data["number"], data["dob"],
            data["identity_id"], data["initiativ_id"], code))
    except Exception as e:
        log.exception("STEP captcha: API xato uid=%s: %s", uid, e)
        return await wait.edit_text("⚠️ Sayt javob bermadi. Bir oz kutib qayta urinib ko'ring.")
    if status == 200 and isinstance(body, dict) and body.get("result"):
        res = body["result"]
        log.info("STEP captcha: ✅ TOPILDI uid=%s fio=%s", uid, res.get("fullname"))
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
            log.exception("STEP oblast: viloyat olishda xato uid=%s: %s", uid, e)
            await msg.answer("⚠️ Viloyatlar olinmadi. Qayta urinib ko'ring: /start")
        return
    err = body.get("error", body) if isinstance(body, dict) else str(body)
    new_b64 = body.get("captcha") if isinstance(body, dict) else None
    if new_b64:
        try:
            save_captcha(uid, base64.b64decode(new_b64), "server_err")
        except Exception:
            pass
    log.warning("STEP captcha: ❌ MOS KELMADI uid=%s status=%s code=%r err=%r guid=%s",
                uid, status, code, err, data.get("request_id"))
    # serverning yangi rasmini saqlab qo'ydik, lekin botda TOZA captcha (yangi guid) yuboramiz —
    # eski guid eskirgan bo'lishi mumkin, shuning uchun har xatoda yangi sessiya
    await wait.delete()
    await msg.answer(texts.CAPTCHA_FAIL)
    await send_captcha(msg, state)

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
    await call.message.answer(texts.ASK_MFY, reply_markup=kb.list_kb("mfy", mfy))
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
    api = api_of(call.from_user.id)
    loop = asyncio.get_event_loop()
    athlete = data.get("athlete", {})
    await call.message.answer("⏳ Sport yo'nalishlari yuklanmoqda...")
    try:
        scode, scats = await loop.run_in_executor(None,
            lambda: api.get_sport_categories(athlete.get("genderid", 1), data["initiativ_id"]))
    except Exception as e:
        log.exception("STEP sportcat: uid=%s xato: %s", call.from_user.id, e)
        return await call.message.answer("⚠️ Sport kategoriyalari olinmadi. Qayta urinib ko'ring: /start")
    if scode != 200 or not isinstance(scats, list):
        log.warning("STEP sportcat: status=%s body=%r", scode, str(scats)[:500])
        return await call.message.answer("⚠️ Sport kategoriyalari olinmadi. Qayta urinib ko'ring: /start")
    await state.update_data(sportcats=scats)
    await state.set_state(Reg.sportcat)
    await call.message.answer(texts.ASK_SPORTCAT, reply_markup=kb.list_kb("scat", scats))
    await call.answer()


@dp.callback_query(F.data.startswith("scat:"))
async def cb_scat(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data.startswith("scat:page:"):
        page = int(call.data.split(":")[-1])
        return await call.message.edit_reply_markup(
            reply_markup=kb.list_kb("scat", data.get("sportcats", []), page))
    scid = int(call.data.split(":")[1])
    scnames = {x["id"]: x.get("name", "?") for x in data.get("sportcats", [])}
    await state.update_data(sportcat_id=scid, sportcat_name=scnames.get(scid, str(scid)))
    api = api_of(call.from_user.id)
    loop = asyncio.get_event_loop()
    athlete = data.get("athlete", {})
    try:
        scode, sports = await loop.run_in_executor(None, lambda: api.get_sport_types(
            athlete.get("genderid", 1), data["initiativ_id"],
            athlete.get("dateofbirth", ""), 0, scid))
    except Exception as e:
        log.exception("STEP sport: uid=%s xato: %s", call.from_user.id, e)
        return await call.message.answer("⚠️ Sport turlari olinmadi. Qayta urinib ko'ring: /start")
    if scode != 200 or not isinstance(sports, list):
        log.warning("STEP sport: status=%s body=%r", scode, str(sports)[:500])
        return await call.message.answer("⚠️ Sport turlari olinmadi. Qayta urinib ko'ring: /start")
    await state.update_data(sports=sports)
    names = "\n".join(f"{i+1}. {s.get('name')}" for i, s in enumerate(sports[:40]))
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
    for tok in (msg.text or "").replace(",", " ").split():
        s = by_idx.get(tok.strip()) or by_id.get(tok.strip())
        if s:
            picks.append(s)
    if not picks:
        return await msg.answer("Topilmadi. Ro'yxatdan raqam yuboring (masalan: 1 yoki 1,2).")
    await state.update_data(sport_ids=[p["id"] for p in picks],
        sport_names=", ".join(p.get("name", "?") for p in picks))
    api = api_of(msg.from_user.id)
    loop = asyncio.get_event_loop()
    athlete = data.get("athlete", {})
    try:
        acode, acats = await loop.run_in_executor(None, lambda: api.get_age_categories(
            athlete.get("genderid", 1), athlete.get("dateofbirth", ""), data["initiativ_id"]))
    except Exception as e:
        log.exception("STEP agecat: uid=%s xato: %s", msg.from_user.id, e)
        return await msg.answer("⚠️ Yosh kategoriyalari olinmadi. Qayta urinib ko'ring: /start")
    if acode != 200 or not isinstance(acats, list) or not acats:
        await state.set_state(Reg.photo)
        return await msg.answer(
            f"Tanlandi: {', '.join(p.get('name','?') for p in picks)}\n\n" + texts.ASK_PHOTO,
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
    aid = int(call.data.split(":")[1])
    anames = {x["id"]: x.get("name", "?") for x in data.get("agecats", [])}
    await state.update_data(agecat_id=aid, agecat_name=anames.get(aid, str(aid)))
    await state.set_state(Reg.photo)
    await call.message.answer(texts.ASK_PHOTO, parse_mode="HTML")
    await call.answer()

@dp.message(Reg.photo, F.photo)
async def m_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    api = api_of(msg.from_user.id)
    bot: Bot = msg.bot
    ph = msg.photo[-1]
    f = await bot.get_file(ph.file_id)
    buf = io.BytesIO()
    await bot.download_file(f.file_path, buf)
    raw = buf.getvalue()
    loop = asyncio.get_event_loop()
    wait = await msg.answer("⏳ Rasm tayyorlanmoqda...")
    # avtomatik siqish: >200KB bo'lsa JPEG sifat/o'lcham kamaytiriladi
    img = await loop.run_in_executor(None, compress_image, raw)
    if len(raw) > 200*1024:
        log.info("STEP photo: uid=%s raw=%dKB -> compressed=%dKB",
                 msg.from_user.id, len(raw)//1024, len(img)//1024)
    try:
        scode, body = await loop.run_in_executor(None, lambda: api.attach_photo(img, "photo.jpg"))
    except Exception as e:
        log.exception("STEP photo: uid=%s yuklanmadi: %s", msg.from_user.id, e)
        return await wait.edit_text("⚠️ Rasm yuklanmadi. Qayta yuborib ko'ring.")
    if scode != 200 or not isinstance(body, dict) or not body.get("id"):
        log.warning("STEP photo: status=%s body=%r", scode, str(body)[:500])
        await wait.delete()
        await state.update_data(photo_file_id="")
        await msg.answer("⚠️ Rasm qabul qilinmadi — rasmsiz davom etamiz.")
    else:
        await wait.delete()
        await state.update_data(photo_file_id=body["id"], photo_info=body)
        await msg.answer("📷 Rasm qabul qilindi.")
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
        return await call.message.answer(texts.CANCELLED, reply_markup=kb.remove_kb())
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
        log.exception("CONFIRM: uid=%s yuborilmadi: %s", call.from_user.id, e)
        return await call.message.answer("⚠️ Yuborilmadi — sayt javob bermadi. Qayta urinib ko'ring.")
    if scode in (200, 201) and (not isinstance(body, dict) or body.get("success", True)):
        phone = data.get("phone", "")
        init = config.INITIATIV_TYPES.get(data.get("initiativ_id"), "")
        extra = {
            "initiativ_id": data.get("initiativ_id"),
            "initiativ_name": init,
            "identity_id": data.get("identity_id"),
            "identity_name": data.get("identity_id") and
                config.IDENTITY_DOCS.get(data.get("identity_id"), ""),
            "oblast_name": data.get("oblast_name", ""),
            "region_name": data.get("region_name", ""),
            "mfy_name": data.get("mfy_name", ""),
            "sportcat_name": data.get("sportcat_name", ""),
            "sport_names": data.get("sport_names", ""),
            "agecat_id": data.get("agecat_id"),
            "agecat_name": data.get("agecat_name", ""),
        }
        await store.save_registration(call.from_user.id, phone, athlete, extra)
        await state.clear()
        await call.message.answer(texts.SENT_OK, reply_markup=kb.more_kb(),
                                  parse_mode="HTML")
    else:
        log.warning("CONFIRM: uid=%s yuborilmadi status=%s body=%r",
                    call.from_user.id, scode, str(body)[:500])
        await call.message.answer(texts.SENT_FAIL)
    await call.answer()


@dp.callback_query(F.data.startswith("more:"))
async def cb_more(call: CallbackQuery, state: FSMContext):
    uid = call.from_user.id
    if call.data == "more:yes":
        await start_flow(uid, call.message, state)
    elif call.data == "more:export":
        await send_excel(uid, call.message)
    else:
        await status_for(uid, call.message)
    await call.answer()


async def on_startup():
    await store.init_db()


async def main():
    debug_dir = debuglog.setup()
    log.info("=== BOT START ===  debug dir: %s", debug_dir)
    if not config.BOT_TOKEN:
        print("BOT_TOKEN topilmadi. .env ga BOT_TOKEN=... qo'shing. Namuna: .env.example")
        raise SystemExit(1)
    log.info("CAPTCHA_PHONE mode=%r  ADMIN_IDS=%s", config.CAPTCHA_PHONE, config.ADMIN_IDS)
    await store.init_db()
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
