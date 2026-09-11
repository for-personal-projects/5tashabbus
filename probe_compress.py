"""compress_image testi: katta rasm yaratib, <200KB ga tushishini tekshirish."""
import io
import os
import random
import sys
sys.path.insert(0, "d:/5tashabbus_bot")
from PIL import Image
from image_utils import compress_image, MAX_BYTES

# 1) Katta tasodifiy rasm yaratamiz (4000x3000, JPEG ~5-8MB bo'lishi kerak)
img = Image.new("RGB", (4000, 3000))
px = img.load()
random.seed(42)
for y in range(0, 3000, 7):
    for x in range(0, 4000, 7):
        px[x, y] = (random.randrange(256), random.randrange(256), random.randrange(256))
buf = io.BytesIO()
img.save(buf, format="JPEG", quality=98)
raw = buf.getvalue()
print("raw size:", len(raw)//1024, "KB")

out = compress_image(raw)
print("compressed:", len(out)//1024, "KB", "| < 200KB:", len(out) <= MAX_BYTES)

# 2) formatsiz/buzilgan bayt — xato bermasdan xom qaytarishi kerak
bad = b"\x00\x01\x02" * 100000
out2 = compress_image(bad)
print("bad input returns raw:", out2 == bad)

# 3) allaqachon kichik rasm — o'zgarmas qaytishi kerak
buf3 = io.BytesIO()
Image.new("RGB", (300, 400), (200, 200, 200)).save(buf3, format="JPEG", quality=85)
small = buf3.getvalue()
print("small unchanged:", compress_image(small) == small, "| size:", len(small)//1024, "KB")

# 4) yaratilgan rasmni haqiqiy fotosuratga o'xshatib yana bir bor
img2 = Image.new("RGB", (1200, 1600), (120, 150, 180))
for y in range(0, 1600, 3):
    for x in range(0, 1200, 3):
        img2.putpixel((x, y), (random.randrange(256),)*3)
b4 = io.BytesIO()
img2.save(b4, format="JPEG", quality=100)
out4 = compress_image(b4.getvalue())
print("1200x1600 q100:", len(b4.getvalue())//1024, "KB ->", len(out4)//1024, "KB",
      "| ok:", len(out4) <= MAX_BYTES)
open("d:/5tashabbus_bot/test_compressed.jpg", "wb").write(out4)
print("COMPRESS_OK")