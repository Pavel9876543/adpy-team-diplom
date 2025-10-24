#!/usr/bin/env python3
"""
скрипт для инициализации БД
хапускать после: docker-compose up -d postgres
"""

from database import init_db, engine


def main():
    print("Инициализация базы данных...")

    try:
        # Создаем таблицы
        init_db()

        # Проверяем созданные таблицы
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print("База данных успешно инициализирована!")
        print(f"Созданные таблицы: {tables}")

    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")
        raise


if __name__ == "__main__":
    main()