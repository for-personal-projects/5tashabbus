import requests
API="https://api.5tashabbus.uz"
H={"User-Agent":"Mozilla/5.0","Origin":"https://5tashabbus.uz","Referer":"https://5tashabbus.uz/"}
s=requests.Session(); s.headers.update(H)
import uuid
for ph in ["+998901234567", "998901234567", "null"]:
    guid=uuid.uuid4().hex[:20]
    r=s.get(API+f"/Account/GenerateCaptcha?id={guid}&phoneNumber={ph}",timeout=20)
    print(repr(ph), r.status_code, r.text[:200])
