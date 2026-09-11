"""Captcha rasmini avtomatik o'qish (Tesseract OCR).

O'rnatish:
  pip install pillow pytesseract
  Windows: https://github.com/UB-Mannheim/tesseract/wiki (Tesseract-OCR)
  Boshqa joyda bo'lsa .env ga: TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

read_captcha(img_bytes) -> "W3RT" ko'rinishidagi satr yoki None.
"""
import io
import os
import shutil
import subprocess

from PIL import Image, ImageOps

WHITELIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

_tess_cmd = None


def find_tesseract():
    """Tesseract bajaruvchi faylini topish (env -> standart joylar -> PATH)."""
    global _tess_cmd
    if _tess_cmd:
        return _tess_cmd
    cand = os.getenv("TESSERACT_CMD", "").strip()
    if cand and os.path.isfile(cand):
        _tess_cmd = cand
        return _tess_cmd
    for p in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Tesseract-OCR\\tesseract.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\\Tesseract-OCR\\tesseract.exe"),
    ):
        if os.path.isfile(p):
            _tess_cmd = p
            return _tess_cmd
    _tess_cmd = shutil.which("tesseract")
    return _tess_cmd


def _prep(img: Image.Image) -> Image.Image:
    """OCR uchun tayyorlash: kulrang + 3x kattalashtirish + kontrast."""
    g = img.convert("L")
    g = g.resize((g.width * 3, g.height * 3), Image.LANCZOS)
    return ImageOps.autocontrast(g)


def _bin(g: Image.Image, thr: int) -> Image.Image:
    return g.point(lambda x: 255 if x > thr else 0)


def _png(img: Image.Image) -> bytes:
    b = io.BytesIO()
    img.save(b, format="PNG")
    return b.getvalue()


def _clean(text: str) -> str:
    """Faqat A-Z va 0-9 qoldirib, KATTA harfga o'tkazamiz."""
    return "".join(c for c in (text or "").upper() if c in WHITELIST)


def read_captcha(img_bytes: bytes):
    """Captcha rasmini o'qish.

    Qaytaradi: 3-6 belgili satr (masalan 'W3RT') yoki None.
    3 xil threshold (140/170/110) va 3 xil PSM (7/8/6) sinab,
    eng ishonchli natijani tanlaydi.
    """
    tess = find_tesseract()
    if not tess:
        return None
    try:
        img = Image.open(io.BytesIO(img_bytes))
    except Exception:
        return None
    g = _prep(img)
    best = None
    for thr in (140, 170, 110):
        v = _bin(g, thr)
        for psm in (7, 8, 6):
            try:
                raw = pytesseract.image_to_string(
                    v, config="--psm %d -c tessedit_char_whitelist=%s" % (psm, WHITELIST))
            except Exception:
                try:
                    raw = subprocess.run(
                        [tess, "stdin", "stdout", "--psm", str(psm),
                         "-c", "tessedit_char_whitelist=" + WHITELIST],
                        input=_png(v), capture_output=True, timeout=25
                    ).stdout.decode("utf-8", "ignore")
                except Exception:
                    continue
            txt = _clean(raw)
            if 3 <= len(txt) <= 6:
                if best is None or abs(len(txt) - 4) < abs(len(best) - 4):
                    best = txt
                if len(txt) == 4:
                    return txt
    return best
