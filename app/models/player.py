from sqlalchemy import Column, Integer, String, ForeignKey

from app.extensions import db


class Player(db.Model):
    __tablename__ = 'registered_players'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    captain = Column(String, nullable=False)
    player_id = Column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)

    def update_captain_status(self, new_status, session):
        self.captain = new_status
        session.commit()