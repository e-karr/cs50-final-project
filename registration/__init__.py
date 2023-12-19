from flask import Flask, render_template, flash
from random import randint
from .models.event import Event
from . import auth, user
from .db import init_db

def create_app():
    
    # Configure application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:////Users/elizabethkarr/cs50/project/registration/kvkl_registration.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TEMPLATES_AUTO_RELOAD=True,
        SESSION_PERMANENT=False,
        SESSION_TYPE="filesystem"
    )

    # Initialize Flask SQLAlchemy
    engine, Session, metadata = init_db(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)

    @app.route("/", methods=["GET"])
    def index():
        """Generate homepage with list of events"""
        events = []
        error = None

        try:
            # Generate list of events
            events = Event.query.all()

            for event in events:
                for team in event.teams:
                    with Session() as session:
                        team.players = team.get_roster(session)
        except Exception as e:
            print(f"An error occurred: {e}")
            error = "An error occured while getting events"


        # Show homepage
        if error:
            flash(error, 'error')

        return render_template("index.html", events=events)
    
    return app
