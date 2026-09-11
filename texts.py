"""Bot matnlari (o'zbek) — qisqa va foydalanuvchiga tushunarli."""

START = (
    "🏅 <b>5 Tashabbus — ro'yxatdan o'tkazish boti</b>\n\n"
    "👇 Boshlash uchun telefon raqamingizni yuboring:"
)
ASK_PHONE_FIRST = (
    "📱 Telefon raqamingizni yuboring\n"
    "(tugma bilan yoki <code>+998901234567</code> ko'rinishida):"
)
ASK_INIT = "2️⃣ Yo'nalishni tanlang:"
ASK_IDOC = "3️⃣ Hujjat turini tanlang:"
ASK_SERIES = "4️⃣ Hujjat seriyasi (masalan <code>I-HR</code>):"
ASK_NUMBER = "5️⃣ Hujjat raqami (masalan <code>0419656</code>):"
ASK_DOB = "6️⃣ Tug'ilgan sana (<code>DD.MM.YYYY</code>, masalan <code>22.06.2014</code>):"
ASK_CAPTCHA = ("7️⃣ Rasmdeki 4 ta belgini katta harfda yuboring.\n"
    "Rasm xira bo'lsa — 🔄 bosing.")
CAPTCHA_FAIL = "❌ Captcha mos kelmadi. Yangi rasm yubordim — qayta kiriting."
NOT_FOUND = "⚠️ Bola topilmadi yoki ma'lumot xato. Qayta urinib ko'ring: /start"
ASK_OBLAST = "8️⃣ Viloyatni tanlang:"
ASK_REGION = "9️⃣ Tuman/shaharni tanlang:"
ASK_MFY = "🔟 Mahallani tanlang:"
ASK_SPORTCAT = "1️⃣1️⃣ Sport kategoriyasini tanlang:"
ASK_SPORT = "1️⃣2️⃣ Sport turini tanlang (raqamini yuboring, bir nechtasini vergul bilan):"
ASK_AGECAT = "1️⃣3️⃣ Yosh kategoriyasini tanlang:"
ASK_PHOTO = "1️⃣4️⃣ Bola rasmini yuboring (rasm avtomatik siqiladi):"
CONFIRM_TMPL = ("📋 <b>Tekshiring:</b>\n\n{athlete}\n🏫 {init}\n"
    "📍 {oblast} / {region} / {mfy}\n🏅 {sport}\n📞 {phone}\n\nYuborilsinmi?")
SENT_OK = ("🎉 Ariza yuborildi!\n\n"
    "Yana bola qo'shish: /start\nRo'yxat: /status · Excel: /export")
SENT_FAIL = "❌ Yuborishda xato. Qayta urinib ko'ring."
NEED_REGISTER = "Avval /start bilan boshlang."
CANCELLED = "🚫 Bekor qilindi. Qayta boshlash: /start"
HELP = ("/start — yangi bola qo'shish\n"
    "/export — Excel fayl\n"
    "/status — ro'yxatdan o'tganlar\n"
    "/cancel — bekor qilish")
STATUS_EMPTY = "📊 Hali hech kim ro'yxatdan o'tmagan.\nBoshlash: /start"
STATUS_HEAD = "📊 <b>Ro'yxatdan o'tganlar: {n} ta</b>\n\n"
EXPORT_EMPTY = "📭 Hali hech kim ro'yxatdan o'tmagan — /start bilan boshlang."
EXPORT_SENT = "📁 Excel fayl tayyor: <b>{n} ta bola</b>."
