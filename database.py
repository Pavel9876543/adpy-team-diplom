from models import Base, User, Photo, Favorite, Blacklist


def create_tables(engine):
    Base.metadata.create_all(engine)