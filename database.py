# database.py
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, unique=True, nullable=False)  # ID пользователя ВК
    first_name = sq.Column(sq.String(50))
    last_name = sq.Column(sq.String(50))
    age = sq.Column(sq.Integer)
    sex = sq.Column(sq.String(8))
    city = sq.Column(sq.String(50))


class Blacklist(Base):
    __tablename__ = "blacklist"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)  # Кто добавил в ЧС
    blocked_vk_id = sq.Column(sq.Integer, nullable=False)  # Кого заблокировали (по vk_id)

    user = relationship("User", foreign_keys=[user_id])


class Favorite(Base):
    __tablename__ = "favorites"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)  # Кто добавил в избранное
    favorite_vk_id = sq.Column(sq.Integer, nullable=False)  # Кого добавили (по vk_id)

    user = relationship("User", foreign_keys=[user_id])


def create_tables(engine):
    Base.metadata.create_all(engine)