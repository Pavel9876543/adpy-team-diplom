#!/usr/bin/env python3
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import create_tables, engine
from sqlalchemy.exc import OperationalError


def main():
    print("🔄 Ожидание базы данных...")

    # Простая задержка перед первым подключением
    time.sleep(3)

    # Попытка с повторениями
    for i in range(5):
        try:
            create_tables()
            print("✅ База данных успешно инициализирована!")
            return
        except OperationalError as e:
            print(f"⏳ Попытка {i + 1}/5: БД еще не готова...")
            time.sleep(3)

    print("Не удалось подключиться к базе данных")
    sys.exit(1)


if __name__ == "__main__":
    main()