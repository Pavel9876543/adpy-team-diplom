import time
from vk_api.longpoll import VkEventType
from db import get_user
from config import longpoll
from handlers import send_msg, safe_delete_msg, keyboard_single_button, create_inline_keyboard
from services import handle_registration, get_users_by_gender


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
                sex_id, age = handle_registration(user_id, msg, user_data_temp)
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

                users = get_users_by_gender(target_age=age, gender=opposite_sex, count_photo=3, max_attempts=250)

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

