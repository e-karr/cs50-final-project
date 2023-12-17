from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, create_engine, MetaData, ForeignKey
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()

Base = db.Model

def init_db(app):
    db.init_app(app)
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
    Session = sessionmaker(bind=engine)

    # Reflect the existing tables from the database
    metadata = MetaData()
    Base.metadata.reflect(bind=engine)

    return engine, Session, metadata

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(Integer, nullable=False)
    password_hash = Column(String, nullable=False)
    gender = Column(String, nullable=False)

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String, nullable=False)
    month = Column(String, nullable=False)
    day = Column(Integer, nullable=False)
    year = Column(String, nullable=False)
    time = Column(String, nullable=False)
    location = Column(String, nullable=False)
    number_teams = Column(Integer, nullable=False)
    spots_available = Column(Integer, nullable=False)

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String, nullable=False)
    sponsor = Column(String, nullable=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    passcode = Column(Integer, nullable=False)


class Player(Base):
    __tablename__ = 'registered_players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    captain = Column(String, nullable=False)
    player_id = Column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
