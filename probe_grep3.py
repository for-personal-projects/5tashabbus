import re
p="d:/5tashabbus_bot/js/chunk-514f6a41.a9682548.js"
t=open(p,encoding="utf-8",errors="ignore").read()
# find guidGenerate, idcaptcha, requestId, filter, Refresh
for kw in ["guidGenerate","idcaptcha","requestId","RefreshReCaptch","GenerateCaptcha","phoneNumber","filter","initiativtypeid","identitydocumentid"]:
    print(f"\n===== {kw} occurrences =====")
    for m in re.finditer(re.escape(kw), t):
        s=max(0,m.start()-800); e=m.end()+800
        ctx=t[s:e].replace("\n"," ")[:1800]
        print("..."+ctx+"...")
        print("---")
        if ctx.count(kw)>5:
            break
    # limit
