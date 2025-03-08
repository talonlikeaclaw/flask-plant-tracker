from app import db


def init_db():
    """Intialize the database"""
    db.create_all()


def drop_db():
    """Drop all tables"""
    db.drop_all()
