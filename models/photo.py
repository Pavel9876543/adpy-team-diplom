import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from .base import Base


class Photo(Base):
    __tablename__ = "photos"

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, sq.ForeignKey("users.vk_id"), nullable=False)
    url = sq.Column(sq.String(100), nullable=False)
    likes_count = sq.Column(sq.Integer, default=0)

    user = relationship("User", foreign_keys=[vk_id])