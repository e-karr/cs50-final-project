from .db import Base
from sqlalchemy import Column, Integer, String, update


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(Integer, nullable=False)
    password_hash = Column(String, nullable=False)
    gender = Column(String, nullable=False)

    @classmethod
    def get_user_by_email(cls, session, email):
        return session.query(cls).filter_by(email=email).first()

    @classmethod
    def get_user_by_id(cls, session, user_id):
        return session.query(cls).filter_by(id=user_id).first()
    
    @classmethod
    def update_first_name(cls, user_id, new_first_name, session):
        stmt = (
            update(cls)
            .where(cls.id == user_id)
            .values(first_name=new_first_name)
        )
        session.execute(stmt)
        session.commit()

    @classmethod
    def update_last_name(cls, user_id, new_last_name, session):
        stmt = (
            update(cls)
            .where(cls.id == user_id)
            .values(last_name=new_last_name)
        )
        session.execute(stmt)
        session.commit()

    @classmethod
    def update_phone_number(cls, user_id, new_phone_number, session):
        stmt = (
            update(cls)
            .where(cls.id == user_id)
            .values(phone_number=new_phone_number)
        )
        session.execute(stmt)
        session.commit()

    @classmethod
    def update_email(cls, user_id, new_email, session):
        stmt = (
            update(cls)
            .where(cls.id == user_id)
            .values(email=new_email)
        )
        session.execute(stmt)
        session.commit()

    @classmethod
    def update_gender(cls, user_id, new_gender, session):
        stmt = (
            update(cls)
            .where(cls.id == user_id)
            .values(gender=new_gender)
        )
        session.execute(stmt)
        session.commit()

    def get_registration_history(self, session):
        from .event import Event
        from .player import Player
        from .team import Team
        history = (session.query(Event.event_name, 
                                Event.month, 
                                Event.day, 
                                Event.time, 
                                Event.location, 
                                Team.team_name, 
                                Team.passcode, 
                                Player.captain, 
                                Team.id
                            )
                            .join(Team, Team.event_id == Event.id)
                            .join(Player, Player.team_id == Team.id)
                            .filter(Player.player_id == self.id)
                            .all())
        return history