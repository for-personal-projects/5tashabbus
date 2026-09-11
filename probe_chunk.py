import html

# 250 ta "bola" bilan status chunk-taking simulyatsiyasi
rows = []
for i in range(250):
    rows.append({"fullname": f"Toshtemirov Rahimjon Alisherovich {i}",
                 "series": "I-HR", "number": f"{i:07d}", "dob": "22.06.2014",
                 "initiativ": "Maktab", "sport": "Shaxmat",
                 "created_at": "2026-09-11 20:00:00"})

phone = "+998901234567"
head = "📊 Ro'yxatdan o'tgan bolalar: {} ta\nProfil: {}\n\n".format(len(rows), html.escape(phone or "—"))
lines = []
for i, r in enumerate(rows, 1):
    nm = html.escape(r.get("fullname", "?") or "?")
    doc = html.escape(f"{r.get('series','')} {r.get('number','')}".strip())
    dob = html.escape(r.get("dob", "") or "")
    ini = html.escape(r.get("initiativ", "") or "")
    sp = html.escape(r.get("sport", "") or "")
    dt = html.escape(r.get("created_at", "") or "")
    extra = " • ".join(x for x in [doc, dob, ini, sp] if x)
    lines.append(f"{i}. <b>{nm}</b>" + (f" — {extra}" if extra else "") + f" <i>({dt})</i>")

chunks, cur = [], head
for ln in lines:
    if len(cur) + len(ln) + 1 > 3900:
        chunks.append(cur)
        cur = ""
    cur += ln + "\n"
if cur.strip():
    chunks.append(cur)

print("chunks:", len(chunks))
print("max len:", max(len(c) for c in chunks))
for idx, c in enumerate(chunks):
    print(idx, len(c), c[:60].replace("\n", " | "), "...", c[-40:].replace("\n", " | "))