import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from .base import Base


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
