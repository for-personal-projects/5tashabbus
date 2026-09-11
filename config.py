import os
from dotenv import load_dotenv
load_dotenv()
API_BASE = os.getenv("API_BASE", "https://api.5tashabbus.uz").rstrip("/")
SITE_BASE = os.getenv("SITE_BASE", "https://5tashabbus.uz").rstrip("/")
LANG = os.getenv("LANG", "uz_latn")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2"))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
IDENTITY_DOCS = {1: "Guvohnoma", 2: "Pasport", 3: "Fuqaroligisiz hujjat", 4: "Chet el hujjati", 5: "ID-karta"}
INITIATIV_TYPES = {1: "Mahalla", 2: "Maktab", 3: "Prof. talim", 4: "Oliy talim", 5: "Vazirlik/idoralar"}
# captcha generatsiya qilishda phoneNumber parametri: "null" | "profile" | ma'lum raqam
# "null" — saytning ro'yxatga kirgan (Login qilmagan) holati, eng xavfsiz
CAPTCHA_PHONE = os.getenv("CAPTCHA_PHONE", "null")
