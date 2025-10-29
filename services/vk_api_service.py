import random
from config import vk_service
from handlers import calculate_age


def get_users_by_gender(target_age, gender=1, count_photo=3, max_attempts=100):
    """
    Поиск случайных пользователей по полу, возрасту, семейному статусу и фото.
    gender: 1 - female, 2 - male
    target_age: возраст пользователя (+/-5 лет)
    count_photo: минимум фото на аватарке
    """
    attempts = 0
    while attempts < max_attempts:
        attempts += 1

        random_user_id = random.randint(1, 1_000_000_000)

        try:
            user_info = vk_service.users.get(
                user_ids=random_user_id,
                fields="sex,bdate,relation,first_name,last_name,is_closed,can_access_closed"
            )
            if not user_info:
                continue

            user = user_info[0]

            # Пропускаем удалённых и заблокированных пользователей
            if user.get("deactivated"):
                continue

            # Закрытые аккаунты — пропускаем
            if user.get("is_closed") and not user.get("can_access_closed"):
                continue

            # Проверяем пол
            if user.get("sex") != gender:
                continue

            # Семейное положение: 0 – не указано, 1 – не женат/не замужем, 6 – в активном поиске
            relation = user.get("relation", 0)
            if relation not in (0, 1, 6):
                continue

            # Проверяем возраст
            age = calculate_age(user.get("bdate"))
            if age is None or abs(age - target_age) > 5:
                continue

            # Фото
            attachments_str = get_top_photos(random_user_id, count_photo)
            if not attachments_str:
                continue

            # Успех
            return {
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "profile_link": f"https://vk.com/id{random_user_id}",
                "attachments": attachments_str
            }

        except Exception:
            continue

    return None


def get_top_photos(target_user_id: int, count: int = 3):
    """Возвращает top-count фото пользователя по количеству лайков."""
    try:
        photos = vk_service.photos.get(
            owner_id=target_user_id,
            album_id='profile',
            extended=1,
            count=50  # берём побольше для сортировки
        )

        photo_list = photos.get('items', [])
        if len(photo_list) < count:
            return None

        # Берём TOP по лайкам
        sorted_photos = sorted(
            photo_list,
            key=lambda x: x.get('likes', {}).get('count', 0),
            reverse=True
        )

        top_photos = sorted_photos[:count]
        attachments = [f"photo{p['owner_id']}_{p['id']}" for p in top_photos]
        return ",".join(attachments)

    except Exception:
        return None