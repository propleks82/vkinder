import sqlalchemy as sq
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from config import db_url


engine = create_engine(db_url)   #, echo=True)
metadata = MetaData()
class Base(DeclarativeBase): pass


class BlackList(Base):
    __tablename__ = 'black_list'
    id = sq.Column(sq.Integer, primary_key=True, index=True)
    profile_id = sq.Column(sq.Integer)
    finded_user_id = sq.Column(sq.Integer)


def add_user(engine, profile_id, finded_user_id):
    with Session(engine) as session:
        to_database = BlackList(profile_id=profile_id, finded_user_id=finded_user_id)
        session.add(to_database)
        session.commit()


def check_user(engine, profile_id, finded_user_id):
    with Session(engine) as session:
        from_database = session.query(BlackList).filter(BlackList.profile_id==profile_id, BlackList.finded_user_id==finded_user_id).first()
        return True if from_database else False


Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=engine)