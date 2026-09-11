"""FSM holatlar: ro'yxatdan o'tkazish bosqichlari."""
from aiogram.fsm.state import State, StatesGroup

class Reg(StatesGroup):
    phone = State()       # 1-qadam: profil telefoni (bolalar shu profildan yuklanadi)
    initiativ = State()
    identity = State()
    series = State()
    number = State()
    dob = State()
    captcha = State()
    found = State()
    oblast = State()
    region = State()
    mfy = State()
    sportcat = State()
    sport = State()
    agecat = State()
    photo = State()
    confirm = State()
    diag_captcha = State()   # admin diagnostikasi uchun
