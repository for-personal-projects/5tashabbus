"""Sayt axios ApiService mantiqi: baseURL + captcha + X-Request-Id."""
import base64
import io
import logging
import random
import string
import time
import requests
import config

log = logging.getLogger("tashabbus")


def _trunc(txt, n=1200):
    txt = str(txt)
    return txt if len(txt) <= n else txt[:n] + f"...[{len(txt)} belgi]"


def make_guid() -> str:
    def chunk():
        s = ""
        while len(s) < 13:
            s += "".join(random.choices(string.ascii_lowercase + string.digits, k=13))
        return s[:13]
    return chunk() + chunk()


class TashabbusApi:
    def __init__(self, lang=None):
        self.lang = lang or config.LANG
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Origin": config.SITE_BASE, "Referer": config.SITE_BASE + "/",
        })
        self.request_id = make_guid()

    def _req(self, method, path, **kw):
        kw.setdefault("timeout", config.REQUEST_TIMEOUT)
        headers = kw.get("headers") or {}
        params = kw.get("params")
        data = kw.get("json") or kw.get("data") or kw.get("files")
        log.debug(">>> %s %s | params=%s | headers=%s | body=%s",
                  method, path, _trunc(params, 800), _trunc(headers, 400),
                  _trunc(data, 600))
        last = None
        for i in range(1, config.MAX_RETRIES + 1):
            try:
                r = self.s.request(method, config.API_BASE + path, **kw)
            except (requests.ConnectionError, requests.Timeout) as e:
                last = e
                log.warning("API %s %s try %d: %s", method, path, i, e)
                time.sleep(config.RETRY_DELAY * i)
                continue
            body_txt = r.text[:1500] if "json" in r.headers.get("Content-Type", "") else f"<binary {len(r.content)}B>"
            log.debug("<<< %s %s | status=%s | %s", method, path, r.status_code, _trunc(body_txt, 1500))
            return r
        raise last

    def new_captcha(self, phone=None):
        """Yangi captcha. CAPTCHA_PHONE: "null" (bezaf) yoki "profile"."""
        self.request_id = make_guid()
        mode = config.CAPTCHA_PHONE
        if mode == "profile" and phone:
            path = f"/Account/GenerateCaptcha?id={self.request_id}&phoneNumber={phone}"
            phone_number = phone
        else:
            path = f"/Account/GenerateCaptcha?id={self.request_id}"
            phone_number = None
        log.info("CAPTCHA new: uid-id=%s phoneNumber=%s mode=%s", self.request_id, phone_number, mode)
        r = self._req("GET", path)
        r.raise_for_status()
        data = r.json()
        img = base64.b64decode(data["result"])
        log.info("CAPTCHA gen: guid=%s img=%dB success=%s", self.request_id, len(img), data.get("success"))
        return self.request_id, img, phone_number

    def get_athlete_info(self, series, number, dob, identity_id, initiativ_id, captcha_text):
        params = {"DocumentSeries": series.strip().upper(),
            "DocumentNumber": number.strip(), "DateOfBirth": dob.strip(),
            "identityDocumentId": identity_id, "lang": self.lang,
            "initiativTypeId": initiativ_id, "captchaText": captcha_text.strip().upper()}
        log.info("SEARCH attempt: guid=%s code=%r params=%s",
                 self.request_id, captcha_text.strip(), _trunc(params, 600))
        r = self._req("POST", "/Account/GetAthleteInfoForRegistration",
            params=params, headers={"X-Request-Id": self.request_id})
        try:
            body = r.json()
        except Exception:
            body = {"success": False, "error": r.text[:500], "status": r.status_code}
        if isinstance(body, dict):
            log.info("SEARCH result: status=%s success=%s error=%r has_result=%s new_captcha=%s",
                     r.status_code, body.get("success"), body.get("error"),
                     bool(body.get("result")), bool(body.get("captcha")))
        else:
            log.info("SEARCH result: status=%s body=%s", r.status_code, _trunc(body, 600))
        return r.status_code, body

    def get_oblasts(self):
        r = self._req("GET", f"/Oblast/GetAll?lang={self.lang}")
        r.raise_for_status()
        return r.json()

    def get_regions(self, oblast_id):
        r = self._req("GET", f"/Region/GetAll?lang={self.lang}&OblastID={oblast_id}")
        r.raise_for_status()
        return r.json()

    def get_mfy(self, region_id):
        r = self._req("GET", f"/Mfy/GetAll?lang={self.lang}&RegionID={region_id}")
        r.raise_for_status()
        return r.json()

    def get_age_categories(self, gender_id, dob, initiativ_id):
        r = self._req("GET", f"/AgeCategory/GetAll?lang={self.lang}&genderid={gender_id}"
                      f"&dateofbirth={dob}&isSeasonDoc=true&initiativtypeid={initiativ_id}"
                      "&isonlineregistration=true&sporttypecategoryid=0&sporttypeid=0")
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, r.text[:2000]

    def get_sport_categories(self, gender_id, initiativ_id, agecat_list=None):
        q = "".join(f"agecategoryIdList={a}&" for a in (agecat_list or []))
        r = self._req("GET", f"/SportTypeCategory/GetAll?lang={self.lang}&agecategoryid=0"
                      f"&isSeasonDoc=true&{q}initiativtypeid={initiativ_id}"
                      f"&genderId={gender_id}&isonlineregistration=true")
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, r.text[:2000]

    def get_sport_types(self, gender_id, initiativ_id, dob="", agecat_id=0, sportcat_id=0):
        r = self._req("GET", f"/SportType/GetAll?lang={self.lang}&dateOfBirth={dob}"
                      f"&genderId={gender_id}&agecategoryid={agecat_id}"
                      f"&sporttypecategoryid={sportcat_id}&isSeasonDoc=true"
                      f"&initiativtypeid={initiativ_id}&isonlineregistration=true&healthtypeid=")
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, r.text[:2000]

    def attach_photo(self, image_bytes: bytes, filename: str = "photo.jpg"):
        import io as _io
        files = {"file": (filename, _io.BytesIO(image_bytes), "image/jpeg")}
        r = self._req("POST", "/FileManage/Attach", files=files,
                      headers={"X-Request-Id": self.request_id})
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, r.text[:2000]

    def insert_registration(self, applicant: dict):
        r = self._req("POST", "/Account/InsertRegistrationOfAthlete", json=applicant,
                      headers={"X-Request-Id": self.request_id,
                               "Content-Type": "application/json;charset=utf-8"})
        try:
            body = r.json()
        except Exception:
            body = {"status": r.status_code, "text": r.text[:2000]}
        return r.status_code, body


def fmt_athlete(a: dict) -> str:
    fio = a.get("fullname") or (str(a.get("familyname", "")) + " " + str(a.get("firstname", "")) + " " + str(a.get("lastname", "")))
    return (f"✅ <b>Bola topildi</b>\n\n"
            f"👤 {fio.strip()}\n"
            f"📅 {a.get('dateofbirth')}\n"
            f"🪪 {a.get('documentseries')} {a.get('documentnumber')}")
