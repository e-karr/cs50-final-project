from ..db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Event(Base):
    __tablename__ = 'events'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String, nullable=False)
    month = Column(String, nullable=False)
    day = Column(Integer, nullable=False)
    year = Column(String, nullable=False)
    time = Column(String, nullable=False)
    location = Column(String, nullable=False)
    number_teams = Column(Integer, nullable=False)
    spots_available = Column(Integer, nullable=False)

    teams = relationship('Team', back_populates='event')

    def update_spots_available(self, session):
        self.spots_available = self.spots_available - 1
        session.commit()