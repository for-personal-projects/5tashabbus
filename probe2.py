import requests, re, os
h={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
base='https://5tashabbus.uz'
# get index html already? re-parse css/js prefetch too
with open("d:/5tashabbus_bot/index.html",encoding="utf-8") as f:
    html=f.read()
all_js=set(re.findall(r'/js/[^"\']+\.js',html))
print("total js refs",len(all_js))
os.makedirs("d:/5tashabbus_bot/js",exist_ok=True)
# download app* first (likely contains logic)
targets=sorted(all_js)
print(targets)
for j in targets:
    try:
        r=requests.get(base+j,headers=h,timeout=30)
        print(j, r.status_code, len(r.content))
        open("d:/5tashabbus_bot/js/"+j.split("/")[-1],"wb").write(r.content)
    except Exception as e:
        print(j,"ERR",e)
print("done")
