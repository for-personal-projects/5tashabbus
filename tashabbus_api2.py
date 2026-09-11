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
    return (f"✅ Bola topildi!\n\n👤 {fio.strip()}\n📅 Tug'ilgan: {a.get('dateofbirth')}\n"
            f"⚧ Jinsi: {a.get('gendername')}\n🪪 Hujjat: {a.get('documentseries')} {a.get('documentnumber')}\n"
            f"🔢 PINFL: {a.get('pinfl')}\n📱 Tel: {a.get('mobilenumber')}\n")
