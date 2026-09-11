import re
p="d:/5tashabbus_bot/js/chunk-514f6a41.a9682548.js"
t=open(p,encoding="utf-8",errors="ignore").read()
i=t.find("SearchbyEGov(){")
print(t[i:i+7000])
print("\n\n=====TEMPLATE captcha part=====\n")
# search template for captcha input binding
for kw in ["filter.text","photoCaptcha","captcha","RefreshReCaptch"]:
    idx=0
    c=0
    while True:
        j=t.find(kw,idx)
        if j==-1 or c>6: break
        print(f"---{kw}---", t[max(0,j-500):j+900][:1500].replace("\n"," ")[:1500])
        idx=j+len(kw); c+=1
