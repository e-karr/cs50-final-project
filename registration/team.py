from .db import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String, nullable=False)
    sponsor = Column(String, nullable=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    passcode = Column(Integer, nullable=False)

    def get_roster(self, session):
        from .account import Account
        from .player import Player
        roster = (session.query(Account.first_name, 
                                Account.last_name, 
                                Account.id, 
                                Player.captain)
                  .join(Player, Player.player_id == Account.id)
                  .filter(Player.team_id == self.id)
                  .all())
        return roster