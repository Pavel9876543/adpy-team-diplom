import os
from datetime import datetime

from dotenv import load_dotenv
import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType

# -------------------- Настройка --------------------
load_dotenv()
TOKEN = os.getenv("VK_BOT_TOKEN")

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Временное хранилище данных пользователей
user_data_temp = {}

# -------------------- Функции --------------------
def send_msg(user_id: int, text: str):
    """Отправка сообщения пользователю"""
    vk.messages.send(user_id=user_id, message=text, random_id=get_random_id())

def get_user_info(user_id: int) -> dict:
    """Получение информации о пользователе из профиля VK"""
    user = vk.users.get(user_ids=user_id, fields="city,sex,bdate")[0]
    bdate = user.get("bdate")  # формат: "DD.MM.YYYY" или "DD.MM"
    age = None
    if bdate and len(bdate.split(".")) == 3:
        year = int(bdate.split(".")[2])
        age = datetime.now().year - year
    return {
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "sex": user.get("sex"),  # 1 — женщина, 2 — мужчина
        "city": user.get("city", {}).get("title"),
        "age": age
    }

def check_missing_fields(user_info: dict, temp_data: dict) -> list:
    """Проверка, каких данных не хватает"""
    missing = []
    if user_info["sex"] == 0 and "sex" not in temp_data:
        missing.append("sex")
    if not user_info["city"] and "city" not in temp_data:
        missing.append("city")
    if user_info["age"] is None and "age" not in temp_data:
        missing.append("age")
    return missing

def request_field(user_id: int, field: str):
    """Запрос у пользователя недостающей информации"""
    prompts = {"sex": "Укажи свой пол (м/ж):", "city": "Укажи свой город:", "age": "Укажи свой возраст (числом):"}
    send_msg(user_id, prompts[field])
    user_data_temp[user_id]["awaiting"] = field

def process_response(user_id: int, msg: str) -> bool:
    """Обработка ответа пользователя на недостающие данные"""
    awaiting = user_data_temp[user_id].get("awaiting")
    if not awaiting:
        return False

    if awaiting == "sex":
        if msg in ["м", "муж", "парень"]:
            user_data_temp[user_id]["sex"] = 2
        elif msg in ["ж", "жен", "девушка"]:
            user_data_temp[user_id]["sex"] = 1
        else:
            send_msg(user_id, "Введи корректно: м/ж")
            return False
    elif awaiting == "city":
        user_data_temp[user_id]["city"] = msg.title()
    elif awaiting == "age":
        if not msg.isdigit() or int(msg) <= 0 or int(msg) > 120:
            send_msg(user_id, "Введи корректный возраст (числом от 1 до 120).")
            return False
        user_data_temp[user_id]["age"] = int(msg)

    del user_data_temp[user_id]["awaiting"]
    return True

# -------------------- Основной цикл --------------------
for event in longpoll.listen():
    if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
        continue

    user_id = event.user_id
    msg = event.text.strip().lower()

    # Инициализация данных пользователя
    if user_id not in user_data_temp:
        user_data_temp[user_id] = {}

    # Если ждём ответ на недостающие данные
    if "awaiting" in user_data_temp[user_id]:
        if not process_response(user_id, msg):
            continue  # ждём корректного ответа

    # Получаем данные из профиля
    user_info = get_user_info(user_id)
    missing = check_missing_fields(user_info, user_data_temp[user_id])

    # Запрашиваем одно недостающее поле, если есть
    if missing:
        request_field(user_id, missing[0])
        continue

    # Все данные есть — используем финальные значения
    sex_id = user_data_temp[user_id].get("sex", user_info["sex"])
    sex = "Жен" if sex_id == 1 else "Муж" if sex_id == 2 else "Не указан"
    city = user_data_temp[user_id].get("city", user_info["city"])
    first_name = user_data_temp[user_id].get("first_name", user_info["first_name"])
    age = user_data_temp[user_id].get("age", user_info["age"])

    send_msg(user_id, f"✅ Здравствуй, {first_name}!\nТвой город: {city}\nТвой пол: {sex}\nТвой возраст: {age}")
    print(user_data_temp)
    user_data_temp.pop(user_id, None)
    print(user_data_temp)

    # --- TODO: здесь можно продолжить с поиском пользователей ---
    # opposite_sex = 1 if final_sex == 2 else 2
    # send_msg(user_id, "🔍 Ищу подходящих людей...")
