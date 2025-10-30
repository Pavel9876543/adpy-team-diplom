import json
import threading
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from config import vk_group


# -------------------- Отправка/удаление сообщений --------------------
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

def keyboard_main_menu():
    """Клавиатура основного меню после регистрации"""
    kb = VkKeyboard(one_time=False)
    kb.add_button("search", color=VkKeyboardColor.PRIMARY)
    kb.add_line()  # переход на новую строку
    kb.add_button("favorites", color=VkKeyboardColor.POSITIVE)
    kb.add_button("blacklist", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

def create_inline_keyboard(buttons: list) -> str:
    """
    Создаёт inline-клавиатуру с callback-кнопками.
    Ограничение: не более 4 кнопок на ряд.

    :param buttons: Список списков с текстом кнопок, например:
                    [["Да", "Нет"], ["Может"]]
    :return: JSON клавиатуры
    """
    kb = VkKeyboard(inline=True)

    for row in buttons:
        for idx, btn_text in enumerate(row):
            if idx > 0:
                kb.add_line()

            kb.add_button(
                label=btn_text,
                color=VkKeyboardColor.PRIMARY,
            )

    return kb.get_keyboard()

