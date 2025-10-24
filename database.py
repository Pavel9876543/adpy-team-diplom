from models import Base, User, Photo, Favorite, Blacklist
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time
from config import settings

# Создаем движок PostgreSQL с настройками для Docker
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Проверяет соединение перед использованием
    echo=False  # Установите True для отладки SQL запросов
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    from models.base import Base
    print("Создание таблиц в PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")

def wait_for_db(max_retries=5, delay=5):
    """Ожидание готовности базы данных"""
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                print("База данных готова!")
                return True
        except OperationalError as e:
            print(f"Ожидание базы данных... (попытка {i+1}/{max_retries})")
            time.sleep(delay)
    raise Exception("Не удалось подключиться к базе данных")

def create_tables(engine):
    Base.metadata.create_all(engine)