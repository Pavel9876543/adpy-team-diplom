import sys
import os

#
# Скрипт для инициализации БД тестовыми данными
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.user import User
from models.photo import Photo
from models.favorite import Favorite


def init_test_data():
    db = SessionLocal()

    try:
        # Создаем тестовых пользователей
        user1 = User(
            username="test_user1",
            email="user1@example.com",
            hashed_password="hashed_password_123"  # В реальном приложении хэшируйте пароли!
        )

        user2 = User(
            username="test_user2",
            email="user2@example.com",
            hashed_password="hashed_password_456"
        )

        db.add_all([user1, user2])
        db.commit()
        db.refresh(user1)
        db.refresh(user2)

        # Создаем тестовые фото
        photo1 = Photo(
            title="Beautiful Landscape",
            description="A beautiful mountain landscape",
            file_path="/photos/landscape1.jpg",
            file_size=2048000,
            user_id=user1.id
        )

        photo2 = Photo(
            title="City View",
            description="Night view of the city",
            file_path="/photos/city1.jpg",
            file_size=1560000,
            user_id=user2.id
        )

        db.add_all([photo1, photo2])
        db.commit()
        db.refresh(photo1)
        db.refresh(photo2)

        # Добавляем в избранное
        favorite = Favorite(
            user_id=user1.id,
            photo_id=photo2.id
        )

        db.add(favorite)
        db.commit()

        print("Тестовые данные успешно добавлены!")

    except Exception as e:
        db.rollback()
        print(f"Ошибка при добавлении тестовых данных: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_test_data()