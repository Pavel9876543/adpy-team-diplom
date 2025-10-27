import os
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from models import Base

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
DB_NAME = os.getenv('DB_NAME')

DSN = f"postgresql://{LOGIN}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

engine = sqlalchemy.create_engine(DSN)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_database():
    """Создает таблицы в БД"""
    Base.metadata.create_all(bind=engine)

def delete_database():
    """Удаляет таблицы в БД"""
    Base.metadata.drop_all(bind=engine)

def get_session():
    """Создание сессии"""
    db = Session()
    return db
