from app.main import bp
from flask import flash, render_template
from app.models.event import Event
from app.extensions import db

@bp.route("/", methods=["GET"])
def index():
    """Generate homepage with list of events"""
    events = []
    error = None

    try:
        # Generate list of events
        events = Event.query.all()

        for event in events:
            for team in event.teams:
                    try:
                        team.players = team.get_roster(db.session)
                    except Exception as e:
                         print(f"An error occured: {e}")
                         error = "An error occured while getting team rosters"
                         db.session.rollback()
    except Exception as e:
        print(f"An error occurred: {e}")
        error = "An error occured while getting events"
        db.session.rollback()


    # Show homepage
    if error:
        flash(error, 'error')

    return render_template("index.html", events=events)