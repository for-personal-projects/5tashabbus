import os, re
jsdir="d:/5tashabbus_bot/js"
for fn in sorted(os.listdir(jsdir)):
    p=os.path.join(jsdir,fn)
    try:
        t=open(p,encoding="utf-8",errors="ignore").read()
    except Exception as e:
        print(fn,"read err",e); continue
    for kw in ["GetAthleteInfoForRegistration","GenerateCaptcha","captchaText","initiativTypeId","identityDocumentId","IsTwoFactorEnabled","GetAllInitiativType","Tshb5EnableANDDisable"]:
        if kw in t:
            print(f"=== {fn} has {kw} ===")
    # detailed context
    if "GetAthleteInfoForRegistration" in t:
        for m in re.finditer(r".{0,600}GetAthleteInfoForRegistration.{0,600}", t):
            print("----CTX----")
            print(m.group(0)[:1500])
            print()
    if "GenerateCaptcha" in t:
        for m in re.finditer(r".{0,600}GenerateCaptcha.{0,600}", t):
            print("----CAPTCHA CTX----")
            print(m.group(0)[:1500])
            print()
