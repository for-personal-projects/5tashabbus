import asyncio
from tashabbus_api import TashabbusApi

async def t():
    import concurrent.futures
    api = TashabbusApi()
    loop = asyncio.get_event_loop()
    rid, img = await loop.run_in_executor(None, api.new_captcha)
    print("captcha ok", rid, len(img))
    open("d:/5tashabbus_bot/captcha_live.png","wb").write(img)
    oblasts = await loop.run_in_executor(None, api.get_oblasts)
    print("oblasts", len(oblasts), oblasts[:2])
    regions = await loop.run_in_executor(None, lambda: api.get_regions(1))
    print("regions TSH", len(regions))
    sc, ac = await loop.run_in_executor(None, lambda: api.get_age_categories(1, "22.06.2014", 2))
    print("agecat", sc, str(ac)[:600])

asyncio.run(t())
print("PROBE OK")
