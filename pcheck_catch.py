t = open("d:/5tashabbus_bot/js/chunk-514f6a41.a9682548.js", encoding="utf-8", errors="ignore").read()
# SearchbyEGov catch / RefreshReCaptch keyin qanday chaqirilayotganini batafsil ko'rish
i = t.find("search-catch")
i = t.find("SearchbyEGov(")
seg = t[i:i+7000]
print(seg[:7000])