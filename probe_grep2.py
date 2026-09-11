import os, re
jsdir="d:/5tashabbus_bot/js"
targets=["d:/5tashabbus_bot/js/chunk-514f6a41.a9682548.js","d:/5tashabbus_bot/js/chunk-68c020be.a7642b5c.js","d:/5tashabbus_bot/js/chunk-0957ca27.3cbb4fd3.js","d:/5tashabbus_bot/js/chunk-40558670.78a06ddb.js"]
for p in targets:
    t=open(p,encoding="utf-8",errors="ignore").read()
    print("="*80)
    print(p, len(t))
    # find all GetAthlete calls with surrounding 2500 chars
    for m in re.finditer(r"GetAthleteInfoForRegistration", t):
        s=max(0,m.start()-3000); e=m.end()+3000
        print(t[s:e][:6000])
        print("\n---CALL SITE END---\n")
