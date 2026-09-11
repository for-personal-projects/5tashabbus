"""Rasmni 200KB gacha siqish (Pillow)."""
import io
from PIL import Image

MAX_BYTES = 200 * 1024   # sayt talabi
TARGET_W = 600           # boshlang'ich kenglik (3x4 fotosurat nisbatiga yaqin)
MIN_QUALITY = 30


def compress_image(raw: bytes, max_bytes: int = MAX_BYTES) -> bytes:
    """JPEG ni ketma-ket sifat/kenglik kamaytirib <200KB qiladi."""
    if len(raw) <= max_bytes:
        return raw
    try:
        img = Image.open(io.BytesIO(raw))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        width, height = img.size
        quality = 90
        while True:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            data = buf.getvalue()
            if len(data) <= max_bytes:
                return data
            quality -= 10
            if quality < MIN_QUALITY:
                # sifat past chegarada — endi o'lchamni kichraytiramiz
                width = int(width * 0.8)
                height = int(height * 0.8)
                if width < 120:   # juda kichik bo'lib qolsa — oxirgi variant
                    return data
                img = img.resize((width, height), Image.LANCZOS)
                quality = 85
    except Exception:
        return raw  # siqib bo'lmasa — xom holda qaytaramiz (yuqorida ogohlantiriladi)