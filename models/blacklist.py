import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from .base import Base


class Blacklist(Base):
    __tablename__ = "blacklist"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)  # Кто добавил в ЧС
    blocked_vk_id = sq.Column(sq.Integer, nullable=False)  # Кого заблокировали (по vk_id)

    user = relationship("User", foreign_keys=[user_id])