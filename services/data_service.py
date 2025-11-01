from db import add_to_user, add_to_favorite, add_to_blacklist, get_all_favorite, get_all_blacklist
from handlers import send_msg, keyboard_single_button, process_response, \
    check_missing_fields, request_field, keyboard_main_menu
from services import get_user_info


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

def save_to_favorites(user_id, favorite_vk_id):
    result_added_favorite = add_to_favorite(user_id, favorite_vk_id)
    if result_added_favorite is None: # Новый случай: ошибка или конфликт
        send_msg(user_id, f"❌ Невозможно добавить в избранное: пользователь находится в черном списке")
    elif result_added_favorite is True: # Уже в избранном
         send_msg(user_id, f"⚠️ Пользователь уже в избранном")
    elif result_added_favorite: # Успешно добавлен (возвращен объект Favorite)
        send_msg(user_id, "✅ Пользователь успешно добавлен в избранное")
    else: # Остальные ошибки (хотя add_to_favorite не должен возвращать False, но на всякий случай)
        send_msg(user_id, "❌ Не удалось добавить пользователя в избранное")

def save_to_blacklist(user_id, blocked_vk_id):
    result_added_favorite = add_to_blacklist(user_id, blocked_vk_id)
    if result_added_favorite is None: # Новый случай: ошибка или конфликт
        send_msg(user_id, f"❌ Невозможно добавить в избранное: пользователь находится в избранном")
    elif result_added_favorite is True: # Уже в черном списке
        send_msg(user_id, f"⚠️ Пользователь уже в черном списке")
    elif result_added_favorite: # Успешно добавлен (возвращен объект Blacklist)
        send_msg(user_id, "✅ Пользователь успешно добавлен в черный список")
    else: # Остальные ошибки
        send_msg(user_id, "❌ Не удалось добавить пользователя в черный список")

def show_favorites(user_id):
    favorites = get_all_favorite(user_id)
    if not favorites:
        send_msg(user_id, "📭 Ваш список избранного пуст",
                 custom_keyboard=keyboard_main_menu())
    else:
        send_msg(user_id, f"💖 Ваше избранное ({len(favorites)} человек):",
                 custom_keyboard=keyboard_main_menu())
        for fav in favorites[:10]:  # ограничиваем вывод
            user_info = get_user_info(fav.favorite_vk_id)
            if user_info:
                profile_link = f"https://vk.com/id{fav.favorite_vk_id}"
                message = f"❤️ {user_info['first_name']} {user_info['last_name']}\n{profile_link}"
                send_msg(user_id, message)

        if len(favorites) > 10:
            send_msg(user_id, f"... и еще {len(favorites) - 10} человек")

def show_blacklist(user_id):
    blacklist = get_all_blacklist(user_id)
    if not blacklist:
        send_msg(user_id, "📭 Ваш черный список пуст",
                 custom_keyboard=keyboard_main_menu())
    else:
        send_msg(user_id, f"🚫 Ваш черный список ({len(blacklist)} человек):",
                 custom_keyboard=keyboard_main_menu())
        for blocked in blacklist[:10]:  # ограничиваем вывод
            user_info = get_user_info(blocked.blocked_vk_id)
            if user_info:
                profile_link = f"https://vk.com/id{blocked.blocked_vk_id}"
                message = f"🚫 {user_info['first_name']} {user_info['last_name']}\n{profile_link}"
                send_msg(user_id, message)

        if len(blacklist) > 10:
            send_msg(user_id, f"... и еще {len(blacklist) - 10} человек")