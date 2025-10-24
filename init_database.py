#!/usr/bin/env python3
"""
скрипт для инициализации БД
хапускать после: docker-compose up -d postgres
"""

import time
import sys
from sqlalchemy.exc import OperationalError

from database import init_db, engine


def wait_for_db(max_retries=10, delay=2):
    """Ожидание готовности БД с простыми ретраями"""
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                print("База данных готова!")
                return True
        except OperationalError:
            print(f"Ожидание БД... ({i + 1}/{max_retries})")
            time.sleep(delay)

    print("Не удалось подключиться к БД")
    return False


if __name__ == "__main__":
    print("Инициализация базы данных...")

    if wait_for_db():
        try:
            init_db()
            print("Таблицы успешно созданы!")
            print("Созданные таблицы: users, photos, favorites, blacklist")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            sys.exit(1)
    else:
        sys.exit(1)