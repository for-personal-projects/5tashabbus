# 5tashabbus_bot — Telegram orqali ro'yxatdan o'tkazish

Sayt (https://5tashabbus.uz) sekin ishlayotgani uchun bot to'g'ridan-to'g'ri
`https://api.5tashabbus.uz` bilan ishlaydi (sayt frontend JS tahlil qilindi).

## Oqim (foydalanuvchi talabiga mos)

/start -> **1) telefon raqam** (profil; bolalar shu profildan yuklanadi) ->
yo'nalish (Maktab/Prof) -> hujjat turi -> seriya (I-HR) -> raqam ->
sana (DD.MM.YYYY) -> captcha rasm (bot yuboradi) -> qidirish ->
viloyat/tuman/mahalla -> sport kategoriya -> sport turi -> yosh kategoriya ->
foto (200KB) -> tasdiqlash -> `InsertRegistrationOfAthlete`

Muvaffaqiyatli yuborilgan har bir bola `registrations.db` (sqlite) ga saqlanadi:
to'liq ma'lumot (athlete + kontekst) `data_json` ustunida birga yoziladi
(familya, ism, sharif, sana, hujjat, PINFL, manzil, sport, telefon va h.k).

## /status  va  /export (Excel)

- `/status` — nechta bola ro'yxatdan o'tgani + ismlari. Ro'yxat uzun bo'lsa
  aynan `4096` harf chegarasidan oshmasligi uchun bo'laklarga (~3900 belgi)
  bo'lib yuboriladi.
- `/export` (yoki `/excel`) — `royxat_<sana>.xlsx` Excel fayl yuboradi.
  Ustunlar: №, Familya, Ism, Sharif, To'liq ism, Tug'ilgan sana, Jinsi,
  Hujjat turi/seriya/raqami, PINFL, Yo'nalish, Viloyat/Tuman/MFY,
  Sport yo'nalishi/Sport turi/Yosh kategoriya,
  **Qaysi raqamdan ro'yxatdan o'tgan**, Bolaning telefoni,
  **Ro'yxatdan o'tgan vaqti**.
- Fayl `exporter.py` (openpyxl) da quriladi; seriya/raqam/PINFL/telefonlar
  matn formati (`@`) bilan yoziladi — bosh nollar/o'sish yeyilmaydi.

## 400 xato sababi (reverse tahlil xulosasi)

- `GenerateCaptcha?id={guid}&phoneNumber=null` — `phoneNumber` bo'sh bo'lsa 400,
  `"null"` yoki profil raqami bo'lishi shart.
- `GetAthleteInfoForRegistration` — `X-Request-Id: {guid}` header bilan yuboriladi
  (sizning `ApiService` parsingizda yo'q edi).
- Noto'g'ri/eskirgan captcha da server 400 + yangi `captcha` (base64) qaytaradi.

## O'rnatish

```powershell
cd d:\5tashabbus_bot
pip install -r requirements.txt
notepad .env        # BOT_TOKEN=... (@BotFather)
python bot.py
```

## Fayllar

- `bot.py` — aiogram 3.x bot (FSM, telefon->...->confirm)
- `tashabbus_api.py` — API klient (retry + headerlar sayt bilan bir xil)
- `store.py` — sqlite (ro'yxatdan o'tgan bolalar, /status uchun)
- `config.py`, `states.py`, `keyboards.py`, `texts.py`
- `js/` — sayt JS lari (tahlil uchun saqlangan, botga kerak emas)
- `probe_*.py` — tahlil/test skriptlari
