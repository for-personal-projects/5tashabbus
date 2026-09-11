"""Profil telefoniga bog'langan captcha + GetAthlete qidiruv testi."""
import sys
sys.path.insert(0, "d:/5tashabbus_bot")
from tashabbus_api import TashabbusApi

api = TashabbusApi()
rid, img, used_phone = api.new_captcha("+998901234567")   # profil telefon bilan
print("captcha ok, rid:", rid, "img bytes:", len(img), "used phone:", used_phone)
# ataylab noto'g'ri captcha yuboramiz — server "Captcha mos kelmadi" 400 bersa demak bog'langan
params_test = dict(series="I-HR", number="0419656", dob="22.06.2014",
                   identity_id=1, initiativ_id=2, captcha_text="XXXX")
st, body = api.get_athlete_info(**params_test)
print("status:", st)
print("body keys:", list(body.keys()) if isinstance(body, dict) else body)
print("error:", body.get("error") if isinstance(body, dict) else "?")
print("new captcha base64 len:", len(body.get("captcha", "")) if isinstance(body, dict) else 0)
print("PROBE_OK")