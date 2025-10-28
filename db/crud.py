from models import User, Favorite, Blacklist, Photo
from db import get_session


# -------------------- Функции для таблицы User--------------------
def add_to_user(user_data: dict) -> User:
    """
    Добавляет запись в таблицу User
    Возвращает объект User
    """
    with get_session() as session:
        try:
            user = User(
                vk_id=user_data['vk_id'],
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                age=user_data.get('age'),
                sex=user_data.get('sex'),
                city=user_data.get('city'),
                music=user_data.get('music'),
                books=user_data.get('books'),
                # groups=user_data.get('groups')
            )
            session.add(user)
            session.commit()
            print(f"✅ Пользователь {user_data['vk_id']} сохранен в БД")
            return type(user).__name__
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка сохранения пользователя: {e}")
            return type(e).__name__


def get_user(vk_id: int):
    """
    Поиск записи в таблице User по атрибуту vk_id
    Возвращает объект User
    """
    with get_session() as session:
        try:
            user = session.query(User).filter(User.vk_id == vk_id).first()
            if user:
                print(f"✅ Найден пользователь: {user.first_name} {user.last_name} (VK ID: {user.vk_id})")
                return user
            else:
                print(f"❌ Пользователь с VK ID {vk_id} не найден")
                return None
        except Exception as e:
            print(f"❌ Ошибка поиска пользователя: {e}")
            return None


def update_user(vk_id: int, update_data: dict) -> bool:
    """
    Обновляет информацию о пользователе в таблице User
    vk_id - VK ID пользователя которого нужно обновить
    update_data - словарь с полями для обновления
    Возвращает True если успешно, False если ошибка
    """
    with get_session() as session:
        try:
            # Кого обновляем, есть ли он в таблице User
            user = session.query(User).filter(User.vk_id == vk_id).first()
            if not user:
                print(f"❌ Пользователь с VK ID {vk_id} не найден")
                return False

            # Обновляем все переданные поля
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
                    print(f"🔄 Обновлено поле {field}: {value}")
                else:
                    print(f"⚠️ Поле {field} не существует в таблице User")

            session.commit()
            print(f"✅ Данные пользователя {vk_id} успешно обновлены")
            return True

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка обновления пользователя: {e}")
            return False


def delete_user(user_vk_id: int) -> bool:
    """
    Удаляет пользователя из таблицы User и все его связанные данные в других таблицах
    Возвращает True если удалено, False если ошибка
    """
    with get_session() as session:
        try:
            # Кого удаляем, есть ли он в таблице User
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return False

            # Удаляем связанные данные из таблиц Favorite, Blacklist, Photo
            session.query(Favorite).filter(Favorite.user_id == user.id).delete()
            session.query(Blacklist).filter(Blacklist.user_id == user.id).delete()
            session.query(Photo).filter(Photo.vk_id == user_vk_id).delete()

            # Удаляем самого пользователя из таблицы User
            session.delete(user)
            session.commit()

            print(f"✅ Пользователь {user_vk_id} и все связанные данные удалены")
            return True

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка удаления пользователя: {e}")
            return False

# -------------------- Функции для таблицы Favorite--------------------
def add_to_favorite(user_vk_id: int, favorite_vk_id: int) -> Favorite:
    """
    Добавляет запись в таблицу Favorite (избранное)
    user_vk_id - кто добавляет в избранное (должен быть в таблице User)
    favorite_vk_id - кого добавляют в избранное
    Возвращает объект Favorite
    """
    with get_session() as session:
        try:
            # Кто добавляет в избранное, есть ли он в таблице User
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return None

            # Проверка на добавление самих себя
            if user_vk_id == favorite_vk_id:
                print("❌ Нельзя добавить себя в избранное")
                return None

            # Проверяем нет ли уже в избранном
            existing_favorite = session.query(Favorite).filter(
                Favorite.user_id == user.id,
                Favorite.favorite_vk_id == favorite_vk_id
            ).first()

            if existing_favorite:
                print(f"⚠️ Пользователь {favorite_vk_id} уже в избранном")
                return existing_favorite

            # Создаем запись в избранном
            favorite = Favorite(
                user_id=user.id,
                favorite_vk_id=favorite_vk_id
            )
            session.add(favorite)
            session.commit()

            print(f"✅ Пользователь {favorite_vk_id} добавлен в избранное пользователя {user_vk_id}")
            return favorite

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка добавления в избранное: {e}")
            return None


def get_all_favorite(user_vk_id: int) -> list:
    """
    Получает всех пользователей из таблицы Favorite (избранное) по user_vk_id
    Возвращает список объектов Favorite
    """
    with get_session() as session:
        try:
            # Находим пользователя
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return []

            # Получаем все записи избранного для этого пользователя
            favorites = session.query(Favorite).filter(
                Favorite.user_id == user.id
            ).all()

            print(f"✅ Найдено {len(favorites)} записей в избранном для пользователя {user_vk_id}")
            return favorites

        except Exception as e:
            print(f"❌ Ошибка получения избранного: {e}")
            return []


def get_favorite_list_favorite_vk_id(user_vk_id: int) -> list:
    """
    Получает только VK ID всех избранных пользователей
    Возвращает список VK ID
    """
    with get_session() as session:
        try:
            # Явно проверяем существование пользователя
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return []

            favorites = get_all_favorite(user_vk_id)
            return [fav.favorite_vk_id for fav in favorites]

        except Exception as e:
            print(f"❌ Ошибка получения списка избранных ID: {e}")
            return []


def delete_from_favorite(user_vk_id: int, favorite_vk_id: int) -> bool:
    """
    Удаляет запись из таблицы Favorite (избранное)
    Возвращает True если удалено, False если ошибка или запись не найдена
    """
    with get_session() as session:
        try:
            # Находим пользователя который удаляет из избранного
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return False

            # Находим запись в избранном для удаления
            favorite = session.query(Favorite).filter(
                Favorite.user_id == user.id,
                Favorite.favorite_vk_id == favorite_vk_id
            ).first()

            if not favorite:
                print(f"⚠️ Пользователь {favorite_vk_id} не найден в избранном пользователя {user_vk_id}")
                return False

            session.delete(favorite)
            session.commit()

            print(f"✅ Пользователь {favorite_vk_id} удален из избранного пользователя {user_vk_id}")
            return True

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка удаления из избранного: {e}")
            return False

# -------------------- Функции для таблицы Blacklist--------------------
def add_to_blacklist(user_vk_id: int, blocked_vk_id: int) -> Blacklist:
    """
    Добавляет запись в таблицу Blacklist (черный список)
    user_vk_id - кто добавляет в черный список (должен быть в таблице User)
    blocked_vk_id - кого добавляют в черный список
    Возвращает объект Blacklist
    """
    with get_session() as session:
        try:
            # Кто добавляет в черный список, есть ли он в таблице User
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return None

            # Проверка на добавление самих себя
            if user_vk_id == blocked_vk_id:
                print("❌ Нельзя добавить себя в черный список")
                return None

            # Проверяем нет ли уже в черном списке
            existing_blacklist = session.query(Blacklist).filter(
                Blacklist.user_id == user.id,
                Blacklist.blocked_vk_id == blocked_vk_id
            ).first()

            if existing_blacklist:
                print(f"⚠️ Пользователь {blocked_vk_id} уже в черном списке")
                return existing_blacklist

            # Создаем запись в черном списке
            blacklisted = Blacklist(
                user_id=user.id,
                blocked_vk_id=blocked_vk_id
            )
            session.add(blacklisted)
            session.commit()

            print(f"✅ Пользователь {blocked_vk_id} добавлен в черный список пользователя {user_vk_id}")
            return blacklisted

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка добавления в черный список: {e}")
            return None


def get_all_blacklist(user_vk_id: int) -> list:
    """
    Получает всех пользователей из таблицы Blacklist (черный список) по user_vk_id
    Возвращает список объектов Blacklist
    """
    with get_session() as session:
        try:
            # Находим пользователя
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return []

            # Получаем все записи черного списка для этого пользователя
            blacklists = session.query(Blacklist).filter(
                Blacklist.user_id == user.id
            ).all()

            print(f"✅ Найдено {len(blacklists)} записей в черном списке для пользователя {user_vk_id}")
            return blacklists

        except Exception as e:
            print(f"❌ Ошибка получения черного списка: {e}")
            return []


def get_blacklist_list_blocked_vk_id(user_vk_id: int) -> list:
    """
    Получает только VK ID всех пользователей в черном списке
    Возвращает список VK ID
    """
    with get_session() as session:
        try:
            # Явно проверяем существование пользователя
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return []

            blacklist = get_all_blacklist(user_vk_id)
            return [blocked.blocked_vk_id for blocked in blacklist]

        except Exception as e:
            print(f"❌ Ошибка получения списка заблокированных ID: {e}")
            return []


def delete_from_blacklist(user_vk_id: int, blocked_vk_id: int) -> bool:
    """
    Удаляет запись из таблицы Blacklist (черный список)
    Возвращает True если удалено, False если ошибка или запись не найдена
    """
    with get_session() as session:
        try:
            # Находим пользователя который удаляет из черного списка
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return False

            # Находим запись в черном списке для удаления
            blacklisted = session.query(Blacklist).filter(
                Blacklist.user_id == user.id,
                Blacklist.blocked_vk_id == blocked_vk_id
            ).first()

            if not blacklisted:
                print(f"⚠️ Пользователь {blocked_vk_id} не найден в черном списке пользователя {user_vk_id}")
                return False

            session.delete(blacklisted)
            session.commit()

            print(f"✅ Пользователь {blocked_vk_id} удален из черного списка пользователя {user_vk_id}")
            return True

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка удаления из черного списка: {e}")
            return False

# -------------------- Функции для таблицы Photo--------------------
def add_photo(user_vk_id: int, photo_url: str, likes_count: int = 0) -> Photo:
    """
    Добавляет запись в таблицу Photo
    user_vk_id - кто добавляет фото в таблицу Photo (должен быть в таблице User)
    photo_url - URL фотографии
    likes_count - количество лайков (по умолчанию 0)
    Возвращает объект Photo
    """
    with get_session() as session:
        try:
            # Кто добавляет в таблицу Photo, есть ли он в таблице User
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return None

            # Проверяем, нет ли уже такого фото
            existing_photo = session.query(Photo).filter(
                Photo.vk_id == user_vk_id,
                Photo.url == photo_url
            ).first()

            if existing_photo:
                print(f"⚠️ Фото {photo_url} уже существует для пользователя {user_vk_id}")
                return existing_photo

            # Создаем запись фото
            photo = Photo(
                vk_id=user_vk_id,
                url=photo_url,
                likes_count=likes_count
            )
            session.add(photo)
            session.commit()

            print(f"✅ Фото добавлено для пользователя {user_vk_id}, ID фото: {photo.id}")
            return photo

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка добавления фото: {e}")
            return None


def get_all_photo(user_vk_id: int) -> list:
    """
    Получает все фотографии  из таблицы Photo по user_vk_id
    Возвращает список объектов Photo
    """
    with get_session() as session:
        try:
            # Находим пользователя
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return []

            # Получаем все фотографии для этого пользователя
            photos = session.query(Photo).filter(
                Photo.vk_id == user_vk_id
            ).all()

            print(f"✅ Найдено {len(photos)} фотографий для пользователя {user_vk_id}")
            return photos

        except Exception as e:
            print(f"❌ Ошибка получения фотографий: {e}")
            return []


def get_photo_list_url(user_vk_id: int) -> list:
    """
    Получает только URL всех фотографий пользователя
    Возвращает список URL фотографий
    """
    with get_session() as session:
        try:
            # Явно проверяем существование пользователя
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return []

            photos = get_all_photo(user_vk_id)
            return [photo.url for photo in photos]

        except Exception as e:
            print(f"❌ Ошибка получения списка URL фотографий: {e}")
            return []


def delete_all_user_photos(user_vk_id: int) -> bool:
    """
    Удаляет все фотографии пользователя из таблицы Photo
    Возвращает True если удалено, False если ошибка
    """
    with get_session() as session:
        try:
            # Находим пользователя
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return False

            photos = session.query(Photo).filter(Photo.vk_id == user_vk_id).all()

            for photo in photos:
                session.delete(photo)

            session.commit()

            print(f"✅ Удалено {len(photos)} фотографий пользователя {user_vk_id}")
            return True

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка удаления всех фото пользователя: {e}")
            return False


def delete_photo_by_url(user_vk_id: int, photo_url: str) -> bool:
    """
    Удаляет конкретное фото по URL
    Возвращает True если удалено, False если ошибка или фото не найдено
    """
    with get_session() as session:
        try:
            # Находим пользователя
            user = session.query(User).filter(User.vk_id == user_vk_id).first()
            if not user:
                print(f"❌ Пользователь {user_vk_id} не найден")
                return False

            # Находим фото для удаления
            photo = session.query(Photo).filter(
                Photo.vk_id == user_vk_id,
                Photo.url == photo_url
            ).first()

            if not photo:
                print(f"⚠️ Фото {photo_url} не найдено для пользователя {user_vk_id}")
                return False

            # Удаляем фото
            session.delete(photo)
            session.commit()

            print(f"✅ Фото удалено для пользователя {user_vk_id}")
            return True

        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка удаления фото: {e}")
            return False