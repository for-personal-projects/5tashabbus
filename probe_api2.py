import base64
import io
import requests
import uuid

API_BASE = "https://api.5tashabbus.uz"
LANG = "uz_latn"

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://5tashabbus.uz",
    "Referer": "https://5tashabbus.uz/",
}

s = requests.Session()
s.headers.update(H)

# captcha olish: id = guid, phoneNumber = null string bo'lishi shart (bo'sh bo'lsa 400 beradi)
guid = uuid.uuid4().hex + uuid.uuid4().hex[:8]
print("GUID:", guid)
r = s.get(f"{API_BASE}/Account/GenerateCaptcha?id={guid}&phoneNumber=null", timeout=20)
print(r.status_code)
print(r.text[:300])
j = r.json()
b64 = j["result"]
print("b64 len", len(b64))
img = base64.b64decode(b64)
open("d:/5tashabbus_bot/captcha_test.png", "wb").write(img)
print("saved captcha_test.png, size", len(img))

# endi ataylab NOTO'G'RI captcha bilan GetAthleteInfo chaqirib body ni ko'ramiz
params = {
    "DocumentSeries": "I-HR",
    "DocumentNumber": "0419656",
    "DateOfBirth": "22.06.2014",
    "identityDocumentId": 1,
    "lang": LANG,
    "initiativTypeId": 2,
    "captchaText": "XXXX",
}
# MUHIM: X-Request-Id header = guid (localStorage idcaptcha)
headers = {"X-Request-Id": guid}
r2 = s.post(f"{API_BASE}/Account/GetAthleteInfoForRegistration", params=params, headers=headers, timeout=20)
print("GetAthlete WRONG captcha:", r2.status_code)
print(r2.text[:3000])

# header siz ham sinaymiz (sizdagi 400 sababi shu bo'lishi mumkin)
r3 = s.post(f"{API_BASE}/Account/GetAthleteInfoForRegistration", params=params, timeout=20)
print("GetAthlete NO header:", r3.status_code)
print(r3.text[:3000])
