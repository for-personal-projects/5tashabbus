import re, glob
for fn in sorted(glob.glob("d:/5tashabbus_bot/js/*.js")):
    c=open(fn,encoding="utf-8",errors="ignore").read()
    if ".Attach(" in c or "FileManage" in c or "InsertRegistrationOfAthlete" in c:
        print("\n"+"="*20+fn+"="*20)
        for pat in ["Attach", "InsertRegistrationOfAthlete", "FileManage/Get"]:
            for m in re.finditer(r".{0,500}"+re.escape(pat)+r".{0,500}", c):
                print(m.group(0)[:1300].replace("\n"," "))
                print("---")
                break
