import re
p="d:/5tashabbus_bot/js/chunk-514f6a41.a9682548.js"
t=open(p,encoding="utf-8",errors="ignore").read()
# Find data section: filter, Applicant defaults
# print around "filter:" and "Applicant:"
for kw in ["filter:", "Applicant:", "data(){return"]:
    print("\n"+"="*30+kw+"="*30)
    for m in re.finditer(re.escape(kw), t):
        print(t[max(0,m.start()-200):m.start()+2500][:3000].replace("},{","}\n{"))
        print("\n---\n")
        break

# SearchbyEGov full method - find from SearchbyEGov to next method
i=t.find("SearchbyEGov")
print(t[i-200:i+9000][:9500])

