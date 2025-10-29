from datetime import datetime
from handlers import send_msg, keyboard_single_button, keyboard_sex


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

def request_field(user_id: int, field: str, user_data_temp):
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

def process_response(user_id: int, msg: str, user_data_temp) -> bool:
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