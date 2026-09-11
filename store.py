"""Ro'yxatdan o'tgan bolalarni saqlash (sqlite, aiosqlite)."""
import json
import os
import aiosqlite

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "registrations.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS registrations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tg_user_id INTEGER NOT NULL,
  phone TEXT NOT NULL DEFAULT '',
  fullname TEXT NOT NULL DEFAULT '',
  familyname TEXT DEFAULT '',
  firstname TEXT DEFAULT '',
  lastname TEXT DEFAULT '',
  series TEXT DEFAULT '',
  number TEXT DEFAULT '',
  dob TEXT DEFAULT '',
  initiativ TEXT DEFAULT '',
  sport TEXT DEFAULT '',
  created_at TEXT DEFAULT (datetime('now','localtime')),
  data_json TEXT DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_reg_user ON registrations(tg_user_id);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        # eski bazaga data_json ustuni qo'shish (migratsiya)
        cur = await db.execute("PRAGMA table_info(registrations)")
        cols = [r[1] for r in await cur.fetchall()]
        if "data_json" not in cols:
            await db.execute("ALTER TABLE registrations ADD COLUMN data_json TEXT DEFAULT '{}'")
        await db.commit()


async def save_registration(tg_user_id: int, phone: str, athlete: dict,
                            extra: dict | None = None) -> int:
    """athlete + extra (kontekst) to'liq json sifatida saqlanadi."""
    await init_db()
    extra = dict(extra or {})
    payload = dict(athlete)
    for k, v in extra.items():
        if v is not None:
            payload[k] = v
    fullname = (athlete.get("fullname") or
                f"{athlete.get('familyname','')} {athlete.get('firstname','')} {athlete.get('lastname','')}".strip())
    initiativ = extra.get("initiativ_name", "")
    sport = extra.get("sport_names", "")
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO registrations (tg_user_id, phone, fullname, familyname, firstname, lastname,"
            " series, number, dob, initiativ, sport, data_json)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (tg_user_id, phone or "", fullname or "",
             athlete.get("familyname", ""), athlete.get("firstname", ""), athlete.get("lastname", ""),
             athlete.get("documentseries", ""), athlete.get("documentnumber", ""),
             athlete.get("dateofbirth", ""), initiativ or "", sport or "",
             json.dumps(payload, ensure_ascii=False, default=str)))
        await db.commit()
        return cur.lastrowid


async def list_registrations(tg_user_id: int):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM registrations WHERE tg_user_id=? ORDER BY id", (tg_user_id,))
        out = []
        for r in await cur.fetchall():
            d = dict(r)
            try:
                d["data_json"] = json.loads(d.get("data_json") or "{}")
            except Exception:
                d["data_json"] = {}
            out.append(d)
        return out


async def count_registrations(tg_user_id: int) -> int:
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM registrations WHERE tg_user_id=?", (tg_user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0
