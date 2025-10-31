import time
from vk_api.longpoll import VkEventType
from db import get_user, get_all_favorite, get_all_blacklist, get_blacklist_list_blocked_vk_id, get_favorite_list_favorite_vk_id
from config import longpoll
from handlers import send_msg, safe_delete_msg, keyboard_single_button, create_inline_keyboard, keyboard_main_menu
from services import handle_registration, get_users_by_gender, save_to_favorites, save_to_blacklist, get_user_info

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
                             custom_keyboard=keyboard_main_menu())

            # -------------------- Поиск людей --------------------
            if msg == 'search':
                if not search_user:
                    # берем только что зарегистрированные данные
                    if sex_id is None or age is None:
                        continue
                else:
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
                    max_attempts=150,
                )

                # Асинхронное удаление сообщения
                safe_delete_msg(msg_id)

                if users:
                    vk_id = users.get('vk_id')
                    keyboard_json = create_inline_keyboard([[f'Добавить в избранное: {vk_id}', f'Добавить в черный список: {vk_id}']])
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
            # -------------------- Просмотр избранного --------------------
            elif msg == 'favorites':
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

            # -------------------- Просмотр черного списка --------------------
            elif msg == 'blacklist':
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

            if msg[:20] == 'добавить в избранное':
                save_to_favorites(user_id, int(msg[22:]))
            elif msg[:24] == 'добавить в черный список':
                save_to_blacklist(user_id, int(msg[26:]))



    except AttributeError as e:
        # защита от редких системных событий longpoll без .text
        continue
    except Exception as e:
        # логируем любые другие ошибки
        print(f"[Error] {e}")
        time.sleep(1)
        continue

