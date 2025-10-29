from db import add_to_user
from handlers import send_msg, keyboard_single_button, process_response, get_user_info, \
    check_missing_fields, request_field


def handle_registration(user_id, msg, user_data_temp):
    """Обрабатывает регистрацию пользователя и возвращает sex_id, age"""
    user_temp = user_data_temp.setdefault(user_id, {})

    if msg != 'start' and "awaiting" not in user_temp:
        send_msg(user_id, "Привет! Это бот для знакомств. Нажми кнопку start, чтобы начать",
                 custom_keyboard=keyboard_single_button('start'))
        return None, None

    if "awaiting" in user_temp and not process_response(user_id, msg, user_data_temp):
        return None, None  # ждём корректного ответа

    user_info = get_user_info(user_id)
    missing = check_missing_fields(user_info, user_temp)
    if missing:
        request_field(user_id, missing[0], user_data_temp)
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