import sys
sys.path.insert(0, "d:/5tashabbus_bot")
t = open("d:/5tashabbus_bot/bot.py", encoding="utf-8").read()
for key in ["API_400_HINT", "NOT_FOUND", "NEED_REGISTER", "texts.START", "ASK_PHONE_FIRST",
            "SENT_FAIL", "EXPORT_SENT", "STATUS_HEAD", "CAPTCHA_FAIL"]:
    print(key, "->", t.count(key))
import texts
for attr in ["START","ASK_PHONE_FIRST","ASK_INIT","ASK_IDOC","ASK_SERIES","ASK_NUMBER","ASK_DOB",
             "ASK_CAPTCHA","CAPTCHA_FAIL","ASK_OBLAST","ASK_REGION","ASK_MFY","ASK_SPORTCAT",
             "ASK_SPORT","ASK_AGECAT","ASK_PHOTO","CONFIRM_TMPL","SENT_OK","SENT_FAIL","CANCELLED",
             "HELP","STATUS_EMPTY","STATUS_HEAD","EXPORT_EMPTY","EXPORT_SENT"]:
    v = getattr(texts, attr, None)
    print(attr, "OK" if v else "MISSING", "|", str(v)[:60].replace("\n", " "))
# bot.py ichida api.5tashabbus yoki x-request kabi texnik so'zlar foydalanuvchi matnida bormi?
for bad in ["api.5tashabbus", "X-Request-Id", "SuccessSend", "idcaptcha"]:
    print("BAD-IN-BOT:", bad, "->", t.count(bad))
print("CHECK_DONE")