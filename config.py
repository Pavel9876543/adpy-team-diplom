import os
import vk_api
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll

# -------------------- Настройка --------------------
load_dotenv()

SERVICE_TOKEN = os.getenv("VK_SERVICE_TOKEN")
GROUP_TOKEN = os.getenv("VK_BOT_TOKEN")

# Сервисный ВК для поиска
vk_service = vk_api.VkApi(token=SERVICE_TOKEN).get_api()

# Групповой ВК для бота
vk_group_session = vk_api.VkApi(token=GROUP_TOKEN)
vk_group = vk_group_session.get_api()
longpoll = VkLongPoll(vk_group_session)