import re, os
jsdir="d:/5tashabbus_bot/js"
for fn in sorted(os.listdir(jsdir)):
    p=os.path.join(jsdir,fn)
    t=open(p,encoding="utf-8",errors="ignore").read()
    if "baseURL" in t or "5tashabbus.uz" in t or "api.service" in t.lower() or "axios" in t.lower():
        print(f"=== {fn} ===")
        for m in re.finditer(r".{0,250}baseURL.{0,250}", t):
            print(m.group(0)[:600].replace("\n"," "))
            print()
        for m in re.finditer(r".{0,250}api\.5tashabbus.{0,250}", t):
            print(m.group(0)[:600].replace("\n"," "))
            print()
        # axios create
        for m in re.finditer(r".{0,200}axios.{0,200}", t):
            ctx=m.group(0)
            if "create" in ctx or "defaults" in ctx:
                print(ctx[:600].replace("\n"," "))
                print()
