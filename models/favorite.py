import sqlalchemy as sq
from sqlalchemy.orm import relationship
from models import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)  # Кто добавил в избранное
    favorite_vk_id = sq.Column(sq.Integer, nullable=False)  # Кого добавили (по vk_id)

    user = relationship("User", foreign_keys=[user_id])
