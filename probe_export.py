"""Excel exporter testi — namunaviy satrlar bilan xlsx qurib o'qish."""
import asyncio
import json
import sys
sys.path.insert(0, "d:/5tashabbus_bot")
import store
import exporter
from openpyxl import load_workbook


async def t():
    await store.init_db()
    uid = 999999
    # eski-jadval uchun qo'lda qo'shilgan satr ham bor sinab ko'ramiz
    rows = [
        {
            "fullname": "Aliyev Ali Valiyevich",
            "series": "I-HR", "number": "0419656",
            "dob": "22.06.2014", "initiativ": "Maktab", "sport": "Futbol",
            "phone": "+998901234567", "created_at": "2026-09-11 20:14:45",
            "data_json": {
                "familyname": "Aliyev", "firstname": "Ali", "lastname": "Valiyevich",
                "fullname": "Aliyev Ali Valiyevich", "dateofbirth": "22.06.2014",
                "gendername": "O'g'il", "identity_name": "Guvohnoma",
                "documentseries": "I-HR", "documentnumber": "0419656", "pinfl": "11506991450123",
                "initiativ_name": "Maktab", "oblast_name": "Toshkent shahri",
                "region_name": "Chilonzor", "mfy_name": "1234-MUSTAQILLIK",
                "sportcat_name": "Futbol", "sport_names": "Futbol 7x7",
                "agecat_name": "2005-2006", "phonenumber": "+998901234567",
                "mobilenumber": "+998901234567",
            },
        },
        {
            "fullname": "Karimov Karim Olimovich",
            "series": "II-HR", "number": "0078123",
            "dob": "24.02.2013", "initiativ": "Maktab", "sport": "Shaxmat",
            "phone": "+998901234567", "created_at": "2026-09-11 20:20:00",
            "data_json": {
                "familyname": "Karimov", "firstname": "Karim", "lastname": "Olimovich",
                "fullname": "Karimov Karim Olimovich", "dateofbirth": "24.02.2013",
                "gendername": "Qiz", "identity_name": "Guvohnoma",
                "documentseries": "II-HR", "documentnumber": "0078123", "pinfl": "17894561230012",
                "initiativ_name": "Maktab", "oblast_name": "Andijon viloyati",
                "region_name": "Asaka tumani", "mfy_name": "556-GULISTON",
                "sportcat_name": "Intellektual", "sport_names": "Shaxmat",
                "agecat_name": "2010-2013", "phonenumber": "+998901234567",
            },
        },
    ]
    data = exporter.build_excel(rows)
    print("xlsx bytes:", len(data))
    open("d:/5tashabbus_bot/test_royxat.xlsx", "wb").write(data)
    wb = load_workbook("d:/5tashabbus_bot/test_royxat.xlsx")
    ws = wb.active
    print("sheet:", ws.title, "dims:", ws.dimensions)
    for row in ws.iter_rows(min_row=1, max_row=4, values_only=True):
        print(" | ".join("" if c is None else str(c) for c in row))

asyncio.run(t())
print("EXPORT_OK")