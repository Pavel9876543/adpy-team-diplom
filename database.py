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
    sex = sq.Column(sq.Integer)
    city = sq.Column(sq.String(50))

    #интересы:
    music = sq.Column(sq.Text)
    books = sq.Column(sq.Text)
    groups = sq.Column(sq.Text)

    favorites = relationship("Favorite", back_populates="user")
    blacklist = relationship("Blacklist", back_populates="user")
    photos = relationship("Photo", back_populates="user")


class Photo(Base):
    __tablename__ = "photos"

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, sq.ForeignKey("users.vk_id"), nullable=False)
    url = sq.Column(sq.String(100), nullable=False)
    likes_count = sq.Column(sq.Integer, default=0)

    user = relationship("User", foreign_keys=[vk_id])

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