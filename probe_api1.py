import requests, uuid
base="https://api.5tashabbus.uz"
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Origin":"https://5tashabbus.uz","Referer":"https://5tashabbus.uz/"}
s=requests.Session()
s.headers.update(H)
# 1) InitiativType
for url in ["/Helper/GetAllInitiativType?lang=uz_latn&isSeasonDoc=true&forOnlineRegistration=true","/Helper/Tshb5EnableANDDisable","/Account/IsTwoFactorEnabled"]:
    try:
        r=s.get(base+url,timeout=20)
        print(url, r.status_code, r.text[:2000])
    except Exception as e:
        print(url,"ERR",e)
# 2) GenerateCaptcha with random guid, no phone
guid=uuid.uuid4().hex[:16]
print("GUID",guid)
try:
    r=s.get(base+f"/Account/GenerateCaptcha?id={guid}&phoneNumber=null",timeout=20)
    print("captcha null phone",r.status_code, r.text[:500], "ctype",r.headers.get("Content-Type"))
    # if image, save
    if r.status_code==200 and "image" in r.headers.get("Content-Type",""):
        open("d:/5tashabbus_bot/captcha_test.png","wb").write(r.content)
        print("saved png",len(r.content))
    else:
        print(r.content[:1000])
except Exception as e:
    print("captcha err",e)
# try with empty phone
try:
    r2=s.get(base+f"/Account/GenerateCaptcha?id={guid}2&phoneNumber=",timeout=20)
    print("captcha empty phone",r2.status_code, r2.text[:1000])
except Exception as e:
    print("captcha2 err",e)
