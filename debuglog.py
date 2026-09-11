"""Debug logging: konsol + faylga (debug.log). DEBUG=1 bo'lsa to'liq yozadi."""
import logging
import os
import sys

DEBUG = os.getenv("DEBUG", "1") == "1"
LOG_DIR = os.getenv("DEBUG_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug"))


def _dir():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(os.path.join(LOG_DIR, "captcha"), exist_ok=True)
    return LOG_DIR


def setup():
    LOG_DIR = _dir()
    root = logging.getLogger()
    if getattr(root, "_dbg_configured", False):
        return LOG_DIR
    root.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    # konsol
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    root.addHandler(ch)
    # fayl
    fh = logging.FileHandler(os.path.join(LOG_DIR, "debug.log"), encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)
    root._dbg_configured = True
    # uchinchi kutubxonalarni jim qilish
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    return LOG_DIR


def save_captcha(uid: int, img: bytes, tag: str = "") -> str:
    LOG_DIR = _dir()
    import time
    fp = os.path.join(LOG_DIR, "captcha", f"u{uid}_{int(time.time())}_{tag or 'x'}.png")
    try:
        with open(fp, "wb") as f:
            f.write(img)
    except Exception:
        return ""
    return fp