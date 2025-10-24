#!/usr/bin/env python3
"""
Тестирование БД для VKinder с очисткой перед тестом
"""
from database import SessionLocal
from models.user import User
from models.photo import Photo
from models.favorite import Favorite
from models.blacklist import Blacklist

def cleanup_test_data():
    """Очистка тестовых данных перед новым тестом"""
    db = SessionLocal()
    try:
        # Удаляем тестовые данные
        db.query(Blacklist).filter(Blacklist.user_id.in_([1, 2, 3])).delete()
        db.query(Favorite).filter(Favorite.user_id.in_([1, 2, 3])).delete()
        db.query(Photo).filter(Photo.vk_id.in_([987654321, 111111111, 777777777])).delete()
        db.query(User).filter(User.vk_id.in_([123456789, 987654321, 111111111, 777777777])).delete()
        db.commit()
        print("Старые тестовые данные очищены")
    except Exception as e:
        db.rollback()
        print(f"При очистке данных: {e}")
    finally:
        db.close()

def test_vkinder_database():
    print("Тестирование БД VKinder...")

    # Очищаем старые тестовые данные
    cleanup_test_data()

    db = SessionLocal()
    try:
        # 1. Создаем основного пользователя VK
        main_user = User()
        main_user.vk_id = 123456789
        main_user.first_name = "Иван"
        main_user.last_name = "Петров"
        main_user.age = 28
        main_user.sex = 2  # 2 - мужской, 1 - женский
        main_user.city = "Москва"
        main_user.music = "Rock, Jazz, Classical"
        main_user.books = "Фантастика, Детективы"
        main_user.groups = "Программирование, Путешествия"

        db.add(main_user)
        db.commit()
        db.refresh(main_user)
        print(f"Основной пользователь создан: {main_user.first_name} {main_user.last_name} (VK ID: {main_user.vk_id})")

        # 2. Создаем пользователя для избранного
        favorite_user = User()
        favorite_user.vk_id = 987654321
        favorite_user.first_name = "Мария"
        favorite_user.last_name = "Сидорова"
        favorite_user.age = 25
        favorite_user.sex = 1  # женский
        favorite_user.city = "Санкт-Петербург"
        favorite_user.music = "Pop, Indie"
        favorite_user.books = "Романы, Поэзия"
        favorite_user.groups = "Искусство, Кино"

        db.add(favorite_user)
        db.commit()
        db.refresh(favorite_user)
        print(f"Пользователь для избранного создан: {favorite_user.first_name} {favorite_user.last_name}")

        # 3. Создаем фото для пользователя
        photo1 = Photo()
        photo1.vk_id = favorite_user.vk_id
        photo1.url = "https://vk.com/photo1_large.jpg"
        photo1.likes_count = 15

        photo2 = Photo()
        photo2.vk_id = favorite_user.vk_id
        photo2.url = "https://vk.com/photo2_large.jpg"
        photo2.likes_count = 23

        db.add_all([photo1, photo2])
        db.commit()
        print(f"Создано 2 фото для пользователя.")

        # 4. Добавляем пользователя в избранное
        favorite = Favorite()
        favorite.user_id = main_user.id
        favorite.favorite_vk_id = favorite_user.vk_id

        db.add(favorite)
        db.commit()
        print("Пользователь добавлен в избранное.")

        # 5. Добавляем пользователя в черный список
        blocked_user = User()
        blocked_user.vk_id = 111111111
        blocked_user.first_name = "Алексей"
        blocked_user.last_name = "Иванов"
        blocked_user.age = 35
        blocked_user.sex = 2
        blocked_user.city = "Екатеринбург"

        db.add(blocked_user)
        db.commit()
        db.refresh(blocked_user)

        blacklist = Blacklist()
        blacklist.user_id = main_user.id
        blacklist.blocked_vk_id = blocked_user.vk_id

        db.add(blacklist)
        db.commit()
        print("Пользователь добавлен в черный список.")

        # 6. Проверяем связи(?) и данные
        users_count = db.query(User).count()
        photos_count = db.query(Photo).count()
        favorites_count = db.query(Favorite).count()
        blacklist_count = db.query(Blacklist).count()

        print(f"\n Статистика БД:")
        print(f"   Пользователей: {users_count}")
        print(f"   Фото: {photos_count}")
        print(f"   В избранном: {favorites_count}")
        print(f"   В черном списке: {blacklist_count}")

        # Проверяем связи(?)
        main_user_favorites = db.query(Favorite).filter(Favorite.user_id == main_user.id).all()
        favorite_user_photos = db.query(Photo).filter(Photo.vk_id == favorite_user.vk_id).all()

        print(f"\n Проверка связей:")
        print(f"   У основного пользователя в избранном: {len(main_user_favorites)} чел.")
        print(f"   Фото избранного пользователя: {len(favorite_user_photos)} шт.")

        # Покажем пример данных
        print(f"\n Пример данных:")
        for fav in main_user_favorites:
            fav_user = db.query(User).filter(User.vk_id == fav.favorite_vk_id).first()
            if fav_user:
                photos = db.query(Photo).filter(Photo.vk_id == fav_user.vk_id).all()
                print(f"   👤 {fav_user.first_name} {fav_user.last_name} - {len(photos)} фото")

        print("\n БД VKinder наконец-то работает !")

    except Exception as e:
        print(f"Ошибка: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_vkinder_database()