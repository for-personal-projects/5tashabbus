import re
p="d:/5tashabbus_bot/js/chunk-514f6a41.a9682548.js"
t=open(p,encoding="utf-8",errors="ignore").read()
# Find InsertRegistrationOfAthlete usage
idx=0
for _ in range(5):
    j=t.find("InsertRegistrationOfAthlete",idx)
    if j==-1: break
    print(t[max(0,j-2500):j+2500][:5500])
    print("\n"+"="*80+"\n")
    idx=j+10

# Find Save / canSave methods
for kw in ["SaveApplicant", "InsertRegistration(", "CheckSMSCode", "SendSMSCode", "GetAllInitiativ", "Tshb5Enable"]:
    j=t.find(kw)
    if j!=-1:
        print(f"---{kw}---")
        print(t[max(0,j-1500):j+2500][:4200])
        print("\n===\n")
