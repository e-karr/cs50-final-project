from .db import Base
from sqlalchemy import Column, Integer, String


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

    def get_teams(self, session):
        from .team import Team
        teams = session.query(Team).filter_by(event_id=self.id).all()
        return teams