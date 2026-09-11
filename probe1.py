import requests, re
h={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
base='https://5tashabbus.uz'
r=requests.get(base+'/',headers=h,timeout=30)
print("len", len(r.text))
js=re.findall(r'src="(/js/[^"]+\.js)"',r.text)
print("found", len(js))
for j in js:
    print(j)
with open("d:/5tashabbus_bot/index.html","w",encoding="utf-8") as f:
    f.write(r.text)
print("saved index")
