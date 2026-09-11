import openpyxl, aiogram, aiosqlite, requests, dotenv
print("deps ok, openpyxl", openpyxl.__version__)
import sys
sys.path.insert(0, "d:/5tashabbus_bot")
import bot
print("bot import OK, lines:", len(open("d:/5tashabbus_bot/bot.py", encoding="utf-8").readlines()))
# exporter ham ishlashini tekshirish
import exporter
print("exporter module OK")