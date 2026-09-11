import re, glob
pats = ["GetParentForRegistration","GetChildrenForRegistration","GetChildrenFromGovData",
        "GetParentFromGovData","GetChildrenFromERP","GetChildrenData","IsUserRegistered",
        "SendSMSCode","CheckSMSCode","GetChildInfo","phoneNumber"]
for fn in sorted(glob.glob("d:/5tashabbus_bot/js/*.js")):
    c = open(fn,encoding="utf-8",errors="ignore").read()
    hits = [p for p in pats if p in c]
    if hits:
        print("="*20, fn.split("\\")[-1], hits)
        for h in hits:
            for m in list(re.finditer(re.escape(h), c))[:3]:
                print(" ---",h,"---")
                print(c[max(0,m.start()-1200):m.end()+1200][:2600].replace("\n"," ")[:2600])
                print()
