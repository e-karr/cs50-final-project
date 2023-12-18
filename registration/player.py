from .db import Base
from sqlalchemy import Column, Integer, String, ForeignKey


class Player(Base):
    __tablename__ = 'registered_players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    captain = Column(String, nullable=False)
    player_id = Column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)