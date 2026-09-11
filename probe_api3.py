import requests
API="https://api.5tashabbus.uz"
H={"User-Agent":"Mozilla/5.0","Origin":"https://5tashabbus.uz","Referer":"https://5tashabbus.uz/"}
s=requests.Session(); s.headers.update(H)
tests=[
 "/Oblast/GetAll?lang=uz_latn",
 "/Region/GetAll?lang=uz_latn&OblastID=1",
 "/Mfy/GetAll?lang=uz_latn&RegionID=1",
 "/Helper/GetAllInitiativType?lang=uz_latn&isSeasonDoc=true&forOnlineRegistration=true",
 "/Helper/GetAllInitiativType?lang=uz_latn&isSeasonDoc=false&forOnlineRegistration=false",
 "/SportTypeCategory/GetAll?lang=uz_latn&agecategoryid=1&isSeasonDoc=true&agecategoryIdList=&initiativtypeid=2&genderId=1&isonlineregistration=true",
 "/Helper/Tshb5EnableANDisable",
 "/Helper/GetTshb5Calendar",
]
for u in tests:
    try:
        r=s.get(API+u,timeout=20)
        print(u,"=>",r.status_code, r.text[:1200])
    except Exception as e:
        print(u,"ERR",e)
