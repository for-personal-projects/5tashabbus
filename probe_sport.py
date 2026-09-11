import re
# chunk-514 qismidan SportType, AgeCategory, Gender endpointlarini topamiz
import glob
for fn in sorted(glob.glob("d:/5tashabbus_bot/js/*.js")):
    c=open(fn,encoding="utf-8",errors="ignore").read()
    if "SportTypeCategory/GetAll" in c or "GetGenderList" in c or "GetHealthTypeList" in c:
        print("\n"+"="*20+fn+"="*20)
        for m in re.finditer(r".{0,400}(SportTypeCategory/GetAll|GetGenderList|GetHealthTypeList|SportType/GetAll|AgeCategory)[^`'\"]*.{0,200}", c):
            print(m.group(0)[:1000].replace("\n"," "))
            print("---")
