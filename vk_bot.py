import time
import logging
from vk_api.longpoll import VkEventType
from db import get_user, get_blacklist_list_blocked_vk_id
from config import longpoll
from handlers import send_msg, safe_delete_msg, create_inline_keyboard, keyboard_main_menu
from services import handle_registration, get_users_by_gender, save_to_favorites, save_to_blacklist
from services import show_favorites, show_blacklist

# Настройка логгера
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),  # лог в файл
    ]
)

# Временное хранилище данных пользователей
user_data_temp = {}

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
                # Если пользователь не зарегистрирован, собираем данные и сохраняем
                sex_id, age = handle_registration(user_id, msg, user_data_temp)
                if sex_id is None or age is None:
                    continue  # ждём следующего события
            elif msg == "start":
                # Если пользователь зарегистрирован, предупреждаем при start
                send_msg(user_id, "⚠️ Пользователь уже зарегистрирован! Нажмите search, чтобы начать поиск",
                         custom_keyboard=keyboard_main_menu())
            # -------------------- Поиск людей --------------------
            elif msg == 'search':
                sex_id = search_user.sex
                age = search_user.age

                blacklist_ids = get_blacklist_list_blocked_vk_id(user_id)
                # favorite_ids = get_favorite_list_favorite_vk_id(user_id)
                exclude_ids = set(blacklist_ids)

                opposite_sex = 1 if sex_id == 2 else 2
                msg_id = send_msg(user_id, "🔍 Ищу подходящих людей...", custom_keyboard=keyboard_main_menu())

                users = get_users_by_gender(
                    target_age=age,
                    exclude_ids=exclude_ids,
                    gender=opposite_sex,
                    count_photo=3,
                    max_attempts=200,
                )

                # Асинхронное удаление сообщения
                safe_delete_msg(msg_id)

                if users:
                    vk_id = users.get('vk_id')
                    keyboard_json = create_inline_keyboard([[f'В избранное: {vk_id}', f'В черный список: {vk_id}']])
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
                        custom_keyboard=keyboard_main_menu()
                    )

            # -------------------- Добавление в избранное --------------------
            elif msg[:11] == 'в избранное':
                save_to_favorites(user_id, int(msg[12:]))

            # -------------------- Добавление в черный список --------------------
            elif msg[:15] == 'в черный список':
                save_to_blacklist(user_id, int(msg[16:]))

            # -------------------- Просмотр избранного --------------------
            elif msg == 'favorites':
                show_favorites(user_id)

            # -------------------- Просмотр черного списка --------------------
            elif msg == 'blacklist':
                show_blacklist(user_id)

            else:
                send_msg(user_id, "Нажмите search, чтобы начать поиск")

    except AttributeError as e:
        # защита от редких системных событий longpoll без .text
        continue
    except Exception as e:
        # логируем любые другие ошибки
        logging.exception(f"[Error] {e}")
        time.sleep(1)
        continue