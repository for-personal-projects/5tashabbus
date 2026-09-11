import asyncio
import store

async def t():
    await store.init_db()
    print("db init ok")
    await store.save_registration(1, "+998901234567",
        {"fullname": "Aliyev Ali", "familyname": "Aliyev", "firstname": "Ali",
         "lastname": "", "documentseries": "I-HR", "documentnumber": "0419656",
         "dateofbirth": "22.06.2014"}, "Maktab", "Futbol")
    await store.save_registration(1, "+998901234567",
        {"fullname": "Karimov Karim", "familyname": "Karimov", "firstname": "Karim",
         "lastname": "", "documentseries": "I-HR", "documentnumber": "0419657",
         "dateofbirth": "22.06.2014"}, "Maktab", "Shaxmat")
    rows = await store.list_registrations(1)
    print("rows", len(rows))
    for r in rows:
        print(r)
    print("count", await store.count_registrations(1))
    # status chunk simulation (4096 limit)
    head = "📊 Ro'yxatdan o'tgan bolalar: {} ta\n\n".format(len(rows))
    lines = [f"{i}. <b>{r['fullname']}</b> — {r['series']} {r['number']} — {r['dob']} <i>({r['created_at']})</i>"
             for i, r in enumerate(rows, 1)]
    chunks, cur = [], head
    for ln in lines:
        if len(cur) + len(ln) + 1 > 3900:
            chunks.append(cur); cur = ""
        cur += ln + "\n"
    if cur.strip():
        chunks.append(cur)
    print("chunks:", len(chunks), "lens:", [len(c) for c in chunks])

asyncio.run(t())
print("STORE_OK")