from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db
from models.account import Account
from models.player import Player

class Team(db.Model):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String, nullable=False)
    sponsor = Column(String, nullable=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    passcode = Column(Integer, nullable=False)

    event = relationship('Event', back_populates='teams')

    def get_roster(self, session):
        
        roster = (
            session.query(Account.first_name, Account.last_name, Player.player_id, Player.captain)
            .join(Player, Player.player_id == Account.id)
            .filter(Player.team_id == self.id)
            .all()
        )
        return roster