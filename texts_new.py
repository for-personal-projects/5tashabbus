"""Bot matnlari (o'zbek)."""
START = (
    "🏅 <b>5 Tashabbus — ro'yxatdan o'tkazish boti</b>\n\n"
    "Sayt sekin ishlayotgani uchun shu bot orqali bolalarni ro'yxatdan o'tkazasiz.\n"
    "Bot sayt bilan bir xil API (<code>api.5tashabbus.uz</code>) ga to'g'ridan-to'g'ri murojaat qiladi.\n\n"
    "👇 Boshlash uchun telefon raqamingizni yuboring:"
)
ASK_PHONE_FIRST = (
    "📱 <b>1-qadam: telefon raqam</b>\n\n"
    "Ro'yxatdan o'tadigan bolalar shu profildan yuklanadi.\n"
    "Raqamni yuboring (masalan <code>+998901234567</code>):"
)
ASK_INIT = "2️⃣ Yo'nalishni tanlang (sayt hozir faqat Maktab va Prof. ta'lim ni online qabul qiladi):"
ASK_IDOC = "3️⃣ Hujjat turini tanlang:"
ASK_SERIES = "4️⃣ Hujjat seriyasini kiriting (masalan <code>I-HR</code>):"
ASK_NUMBER = "5️⃣ Hujjat raqamini kiriting (masalan <code>0419656</code>):"
ASK_DOB = "6️⃣ Tug'ilgan sanani kiriting (<code>DD.MM.YYYY</code>, masalan <code>22.06.2014</code>):"
ASK_CAPTCHA = ("7️⃣ Rasmdeki <b>4 ta harfni</b> katta harfda yozib yuboring.\n"
    "Rasm xira bo'lsa «🔄 Yangi rasm» ni bosing.")
CAPTCHA_FAIL = "❌ Captcha mos kelmadi. Yangi rasm yubordim — qayta kiriting."
NOT_FOUND = "⚠️ Bola topilmadi yoki ma'lumot xato. Qayta urinib ko'ring: /start"
API_400_HINT = ("\n\n<i>400 xatolik sabablari (sayt tahlilidan):</i>\n"
    "• captcha eskirgan/yangilangan — yangi rasm oling\n"
    "• sana formati <code>DD.MM.YYYY</code> bo'lishi shart\n"
    "• seriya/raqam hujjat turiga mos bo'lishi shart\n"
    "• <code>X-Request-Id</code> captcha id bilan bir xil bo'lishi shart (bot buni avtomatik qiladi)")
ASK_OBLAST = "8️⃣ Viloyatni tanlang:"
ASK_REGION = "9️⃣ Tuman/shaharni tanlang:"
ASK_MFY = "🔟 Mahallani tanlang:"
ASK_SPORTCAT = "1️⃣1️⃣ Sport yo'nalish kategoriyasini tanlang:"
ASK_SPORT = "1️⃣2️⃣ Sport turini tanlang (raqamini yuboring, vergul bilan bir nechtasini ham bo'ladi):"
ASK_AGECAT = "1️⃣3️⃣ Yosh kategoriyasini tanlang:"
ASK_PHOTO = "1️⃣4️⃣ Bola rasmini yuboring (jpg, 200KB gacha — sayt talabi):"
CONFIRM_TMPL = ("📋 <b>Tekshiring va yuboring:</b>\n\n{athlete}\n🏫 Yo'nalish: {init}\n"
    "📍 {oblast} / {region} / {mfy}\n🏅 Sport: {sport}\n📞 Tel: {phone}\n\nYuborilsinmi?")
SENT_OK = ("🎉 Ariza yuborildi! Saytdagi «SuccessSend» javobi olindi.\n\n"
    "Yana bola qo'shish uchun /start ni bosing.\nHozirgacha: /status")
SENT_FAIL = "❌ Yuborishda xato: {err}"
NEED_REGISTER = "Avval /start bilan boshlang."
CANCELLED = "🚫 Bekor qilindi. Qayta boshlash: /start"
HELP = ("/start — yangi bola qo'shish (1-qadam: telefon)\n"
    "/register — xuddi /start kabi\n"
    "/cancel — bekor qilish\n/status — nechta bola ro'yxatdan o'tgani + ismlari\n"
    "Sayt: https://5tashabbus.uz\nAPI: https://api.5tashabbus.uz")
STATUS_EMPTY = ("📊 Hali hech qaysi bola ro'yxatdan o'tmagan.\nBoshlash: /start")
STATUS_HEAD = "📊 <b>Ro'yxatdan o'tgan bolalar: {n} ta</b>\nProfil: {phone}\n\n"
