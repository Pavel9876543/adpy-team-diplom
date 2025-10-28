import os
from datetime import datetime
import random
import threading
import time

from dotenv import load_dotenv
import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from db import add_to_user, get_user

# -------------------- Настройка --------------------
load_dotenv()
SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")
GROUP_TOKEN = os.getenv("VK_BOT_TOKEN")

# Сервисный ВК для поиска
vk_service = vk_api.VkApi(token=SERVICE_TOKEN).get_api()

# Групповой ВК для бота
vk_group_session = vk_api.VkApi(token=GROUP_TOKEN)
vk_group = vk_group_session.get_api()
longpoll = VkLongPoll(vk_group_session)

# Временное хранилище данных пользователей
user_data_temp = {}

# -------------------- Функции --------------------
def safe_delete_msg(message_id):
    """Удаляет сообщение асинхронно, чтобы longpoll не падал"""

    def delete():
        try:
            vk_group.messages.delete(message_ids=message_id, delete_for_all=1)
        except Exception as e:
            print(f"[Delete error] {e}")

    threading.Thread(target=delete, daemon=True).start()

def send_msg(user_id: int, text: str, attachments: str = None, custom_keyboard=None):
    """Отправка сообщения пользователю"""
    try:
        return vk_group.messages.send(
            user_id=user_id,
            message=text,
            attachment=attachments,
            random_id=get_random_id(),
            keyboard=custom_keyboard
        )
    except Exception as e:
        print(f"[Send message error] {e}")

# -------------------- Keyboards --------------------
def keyboard_single_button(btn_text: str):
    kb = VkKeyboard(one_time=False)
    kb.add_button(btn_text, color=VkKeyboardColor.POSITIVE)
    return kb.get_keyboard()

def keyboard_sex():
    kb = VkKeyboard(one_time=True)
    kb.add_button("Мужской", color=VkKeyboardColor.PRIMARY)
    kb.add_button("Женский", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()


def create_inline_keyboard(buttons: list, one_time: bool = False) -> str:
    """
    Создаёт inline-клавиатуру с произвольными кнопками.
    Ограничение: не более 4 кнопок на ряд.

    :param buttons: Список списков с текстом кнопок, например:
                    [["Да", "Нет"], ["Может"]]
    :param one_time: Одноразовая клавиатура
    :return: JSON клавиатуры
    """
    kb = VkKeyboard(one_time=one_time, inline=True)

    for row in buttons:
        for idx, btn_text in enumerate(row):
            if idx > 0:
                kb.add_line()  # новая линия между кнопками ряда
            kb.add_button(btn_text, color=VkKeyboardColor.PRIMARY)
    return kb.get_keyboard()

# -------------------- Работа с пользователем --------------------
def get_user_info(user_id: int) -> dict:
    """Получение информации о пользователе из профиля VK"""
    try:
        user = vk_group.users.get(user_ids=user_id, fields="city,sex,bdate,books,music")[0]
    except Exception as e:
        print(f"[get_user_info error] {e}")
        return {}

    bdate = user.get("bdate")
    age = calculate_age(bdate)

    return {
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "sex": user.get("sex"),  # 1 — женщина, 2 — мужчина
        "city": user.get("city", {}).get("title"),
        "age": age,
        "books": user.get("books"),
        "music": user.get("music")
    }

def calculate_age(bdate_str: str):
    """Вычисляем возраст по строке bdate 'DD.MM.YYYY'"""
    if not bdate_str or len(bdate_str.split(".")) != 3:
        return None
    try:
        birth_date = datetime.strptime(bdate_str, "%d.%m.%Y")
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return None

def check_missing_fields(user_info: dict, temp_data: dict) -> list:
    """Проверка, каких данных не хватает"""
    missing = []
    if user_info.get("sex") == 0 and "sex" not in temp_data:
        missing.append("sex")
    if not user_info.get("city") and "city" not in temp_data:
        missing.append("city")
    if user_info.get("age") is None and "age" not in temp_data:
        missing.append("age")
    return missing

def request_field(user_id: int, field: str):
    """Запрос у пользователя недостающей информации"""
    prompts = {
        "sex": "Укажи свой пол (м/ж):",
        "city": "Укажи свой город:",
        "age": "Укажи свой возраст (числом):"
    }
    if field == "sex":
        send_msg(user_id, prompts[field], custom_keyboard=keyboard_sex())
    else:
        send_msg(user_id, prompts[field], custom_keyboard=keyboard_single_button("start"))
    user_data_temp.setdefault(user_id, {})["awaiting"] = field

def process_response(user_id: int, msg: str) -> bool:
    """Обработка ответа пользователя на недостающие данные"""
    awaiting = user_data_temp.get(user_id, {}).get("awaiting")
    if not awaiting:
        return False

    msg = msg.lower().strip()
    if awaiting == "sex":
        if msg in ["м", "муж", "парень", "мужской"]:
            user_data_temp[user_id]["sex"] = 2
        elif msg in ["ж", "жен", "девушка", "женский"]:
            user_data_temp[user_id]["sex"] = 1
        else:
            send_msg(user_id, "Выберите пол, нажав на кнопку ниже:", custom_keyboard=keyboard_sex())
            return False
    elif awaiting == "city":
        user_data_temp[user_id]["city"] = msg.title()
    elif awaiting == "age":
        if not msg.isdigit() or int(msg) <= 0 or int(msg) > 120:
            send_msg(user_id, "Введи корректный возраст (числом от 1 до 120).", custom_keyboard=keyboard_single_button("start"))
            return False
        user_data_temp[user_id]["age"] = int(msg)

    # удаляем ожидание после корректного ответа
    user_data_temp[user_id].pop("awaiting", None)
    return True

def get_users_by_gender(target_age, gender=1, count=3, max_attempts=100):
    """
    gender: 1 - female, 2 - male
    count: минимальное количество фотографий профиля
    target_age: возраст, с которым сравниваем (+/-5 лет)
    max_attempts: сколько случайных user_id попробовать
    """
    attempts = 0
    while attempts < max_attempts:
        attempts += 1

        # Генерируем случайный user_id
        random_user_id = random.randint(1, 500_000_000)

        try:
            # Добавили поле relation
            user_info = vk_service.users.get(
                user_ids=random_user_id,
                fields="sex,bdate,relation"
            )
            user = user_info[0]

            # Проверяем пол
            if user.get("sex") != gender:
                continue

            # Проверяем семейное положение
            relation = user.get("relation", 0)
            if relation not in (0, 1, 6):
                continue

            # Проверяем возраст
            bdate = user.get("bdate")
            age = calculate_age(bdate)
            if age is None:
                continue
            if abs(age - target_age) > 5:
                continue

            # Получаем фотографии профиля
            photos_resp = vk_service.photos.get(
                owner_id=random_user_id,
                album_id='profile',
                count=count,
                photo_sizes=1
            )
            photos = photos_resp.get('items', [])
            if len(photos) < count:
                continue

            # attachments
            attachments = [f"photo{p['owner_id']}_{p['id']}" for p in photos]
            attachments_str = ",".join(attachments)

            # Ссылка
            profile_link = f"https://vk.com/id{random_user_id}"

            return {
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "profile_link": profile_link,
                "attachments": attachments_str
            }

        except vk_api.exceptions.VkApiError:
            continue

    return None

def handle_registration(user_id, msg):
    """Обрабатывает регистрацию пользователя и возвращает sex_id, age"""
    user_temp = user_data_temp.setdefault(user_id, {})

    if msg != 'start' and "awaiting" not in user_temp:
        send_msg(user_id, "Привет! Это бот для знакомств. Нажми кнопку start, чтобы начать",
                 custom_keyboard=keyboard_single_button('start'))
        return None, None

    if "awaiting" in user_temp and not process_response(user_id, msg):
        return None, None  # ждём корректного ответа

    user_info = get_user_info(user_id)
    missing = check_missing_fields(user_info, user_temp)
    if missing:
        request_field(user_id, missing[0])
        return None, None

    # Собираем финальные данные
    final_data = {key: user_temp.get(key, user_info.get(key)) for key in
                  ["first_name", "last_name", "age", "sex", "city", "music", "books"]}

    db_data = {
        'vk_id': user_id,
        'first_name': final_data["first_name"],
        'lastname': final_data["last_name"],
        'age': final_data["age"],
        'sex': final_data["sex"],
        'city': final_data["city"],
        'music': final_data["music"],
        'books': final_data["books"]
    }

    save_status = add_to_user(db_data)
    if save_status == 'User':
        send_msg(user_id, "✅ Данные успешно сохранены! Нажмите search, чтобы начать поиск",
                 custom_keyboard=keyboard_single_button('search'))
    elif save_status == 'IntegrityError':
        send_msg(user_id, "⚠️ Пользователь уже зарегистрирован", custom_keyboard=keyboard_single_button('search'))

    user_data_temp.pop(user_id, None)
    return final_data["sex"], final_data["age"]


# -------------------- Основной цикл --------------------
while True:
    try:
        for event in longpoll.listen():
            # Фильтруем системные события
            if event.type != VkEventType.MESSAGE_NEW or not event.to_me or not hasattr(event, 'text'):
                continue

            user_id = event.user_id
            msg = event.text.strip().lower()

            search_user = get_user(user_id)

            sex_id, age = None, None

            # -------------------- Проверка на регистрацию --------------------
            if not search_user:
                sex_id, age = handle_registration(user_id, msg)
                if sex_id is None or age is None:
                    continue  # ждём следующего события
            else:
                # Если пользователь зарегистрирован, предупреждаем при start
                if msg == "start":
                    send_msg(user_id, "⚠️ Пользователь уже зарегистрирован! Нажмите search, чтобы начать поиск",
                             custom_keyboard=keyboard_single_button('search'))

            # -------------------- Поиск людей --------------------
            if msg == 'search':
                if not search_user:
                    # берем только что зарегистрированные данные
                    if sex_id is None or age is None:
                        continue
                else:
                    sex_id = search_user.sex
                    age = search_user.age

                opposite_sex = 1 if sex_id == 2 else 2
                msg_id = send_msg(user_id, "🔍 Ищу подходящих людей...", custom_keyboard=keyboard_single_button('search'))

                users = get_users_by_gender(target_age=age, gender=opposite_sex, count=3, max_attempts=250)

                # Асинхронное удаление сообщения
                safe_delete_msg(msg_id)

                if users:
                    keyboard_json = create_inline_keyboard([['Добавить в избранное', 'Добавить в черный список']])
                    send_msg(
                        user_id,
                        f"{users['first_name']} {users['last_name']}\n\n{users['profile_link']}",
                        users['attachments'],
                        custom_keyboard=keyboard_json
                    )
                else:
                    send_msg(
                        user_id,
                        "К сожалению, не удалось никого найти(",
                        custom_keyboard=keyboard_single_button('search')
                    )

    except AttributeError:
        # защита от редких системных событий longpoll без .text
        continue
    except Exception as e:
        # логируем любые другие ошибки
        print(f"[Error] {e}")
        time.sleep(1)
        continue

