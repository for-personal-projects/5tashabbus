import re, glob
for fn in sorted(glob.glob("d:/5tashabbus_bot/js/*.js")):
    c=open(fn,encoding="utf-8",errors="ignore").read()
    if "phoneNumber" in c:
        print("\n"+"="*30+fn+"="*30)
        for m in re.finditer(r".{0,700}phoneNumber.{0,700}", c):
            ctx=m.group(0)
            # filter interesting: localStorage, GenerateCaptcha, SendSMS
            if "localStorage" in ctx or "GenerateCaptcha" in ctx or "SendSMS" in ctx or "CheckSMS" in ctx:
                print(ctx.replace(";", ";\n")[:2000])
                print("\n---\n")
                break
        # count
        print("total phoneNumber hits:", c.count("phoneNumber"))
