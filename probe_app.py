t=open("d:/5tashabbus_bot/js/app~e2550e02.4f460aea.js",encoding="utf-8",errors="ignore").read()
print(t[:8000])
print("\n\n---TAIL---\n")
# search for const B =
i=t.find("const B=")
print(t[i:i+2000])
# also find mountInterceptor definition
import re, os, glob
for fn in sorted(glob.glob("d:/5tashabbus_bot/js/*.js")):
    c=open(fn,encoding="utf-8",errors="ignore").read()
    if "mountInterceptor" in c:
        print("\n===",fn,"===")
        for m in re.finditer(r".{0,1200}mountInterceptor.{0,1200}", c):
            print(m.group(0)[:3000].replace(";", ";\n")[:3000])
            print("\n---\n")
