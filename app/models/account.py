from sqlalchemy import Column, Integer, String

from app.extensions import db


class Account(db.Model):
    __tablename__ = 'accounts'
    __table_args__ = {'extend_existing': True}

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

    @staticmethod
    def validate_password(password1, password2):
        error = None

        special_characters = ['$', '#', '@', '!', '*']

        if password1 != password2:
            error = "Password confirmation doesn't match."
        if len(password1) < 8:
            error = "Password must be at least 8 characters."
        if not any(i.isdigit() for i in password1):
            error = "Password must contain at least one number."
        if not any(j.isupper() for j in password1):
            error = "Password must contain at least one capital letter."
        if not any(k in special_characters for k in password1):
            error = "Password must contain at least one special character ($, #, @, !, *)."

        return error

    @staticmethod
    def validate_phone_number(phone_number):
        error = None

        if not phone_number.isdigit():
            error = "Phone number must only contain numbers."
        
        return error
    
    def update_first_name(self, new_first_name, session):
        self.first_name = new_first_name
        session.commit()

    def update_last_name(self, new_last_name, session):
        self.last_name = new_last_name
        session.commit()

    def update_phone_number(self, new_phone_number, session):
        self.phone_number = new_phone_number
        session.commit()

    def update_email(self, new_email, session):
        self.email = new_email
        session.commit()

    def update_gender(self, new_gender, session):
        self.gender = new_gender
        session.commit()

    def update_password(self, new_password_hash, session):
        self.password_hash = new_password_hash
        session.commit()

    def get_registration_history(self, session):
        from .event import Event
        from .player import Player
        from .team import Team
        raw_history = (session.query(Event.event_name, 
                                Event.month, 
                                Event.day,
                                Event.year, 
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
        
        history = []
        for event_name, month, day, year, time, location, team_name, passcode, captain, team_id in raw_history:
            try:
                team_instance = Team.query.get(team_id)
                team_instance.players = team_instance.get_roster(session)

                # Append a tuple with all the information including players
                history.append((event_name, month, day, year, time, location, team_name, passcode, captain, team_id, team_instance.players))
            except Exception as e:
                print(f"Error getting roster for team {team_id}: {e}")
        
        return history
    
    def delete_account(self, session):
        session.delete(self)
        session.commit()