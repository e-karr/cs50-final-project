from flask import Flask, render_template
from random import randint



def create_app():
    from .models.event import Event
    from . import auth, user
    from .db import init_db

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

        try:
            # Generate list of events
            events = Event.query.all()

            # Get teams signed up for events
            for event in events:
                with Session() as session:
                    event.teams = event.get_teams(session)

            for event in events:
                for team in event.teams:
                    with Session() as session:
                        team.players = team.get_roster(session)
        except Exception as e:
            print(f"An error occurred: {e}")

        # Show homepage
        return render_template("index.html", events=events)
    
    return app




# @app.route("/team_register", methods=["GET", "POST"])
# @login_required
# def team_register():
#     """Register a new team"""

#     # Select contact info from logged in user
#     captain = db.execute("""SELECT email, first_name, last_name, phone_number 
#                             FROM accounts WHERE id = ?""", 
#                             session["user_id"])

#     # User reached route via GET
#     if request.method == "GET":
        
#         # Select events from events table
#         events = db.execute("SELECT * FROM events")
        
#         return render_template("team_register.html", events=events, captain=captain)

#     #User reached route via POST

#     # Generate random 6-digit passcode
#     passcode = randint(100000, 999999)
    
#     # Validate form inputs
#     event_id = int(request.form.get("event"))
#     team_name = request.form.get("teamname")
#     sponsor = request.form.get("sponsor")
#     first_name = request.form.get("firstname")
#     last_name = request.form.get("lastname")
#     phone_number = request.form.get("phonenumber")
#     email = request.form.get("email")

#     if not event_id:
#         flash("Must select an event.", "error")
#         return redirect("/team_register")

#     if not team_name:
#         flash("Must enter a team name.", "error")
#         return redirect("/team_register")

#     if not first_name:
#         flash("Must enter a first name.", "error")
#         return redirect("/team_register")

#     if not last_name:
#         flash("Must enter a last name.", "error")
#         return redirect("/team_register")

#     if not phone_number:
#         flash("Must enter a phone number.", "error")
#         return redirect("/team_register")

#     if not phone_number.isdigit():
#         flash("Phone number must only contain numbers.", "error")
#         return redirect("/team_register")

#     if not email:
#         flash("Must enter an email.", "error")
#         return redirect("/team_register")

#     if len(db.execute("""SELECT team_name 
#                          FROM teams 
#                          WHERE team_name = ? 
#                          AND event_id = ?""", 
#                          team_name, event_id)) != 0:
#         flash("This team is already registered", "error")
#         return redirect("/team_register")

#     # Check that player isn't already registered for event
#     event_name = db.execute("SELECT event_name FROM events WHERE id = ?", event_id)
#     if len(db.execute("""SELECT * 
#                          FROM registered_players 
#                          WHERE player_id = ? 
#                          AND event_id = ?""", 
#                          session["user_id"], event_id)) != 0:
#         flash("You are already registered for %s." % (event_name[0])["event_name"], "error")
#         return redirect("/team_register")

#     # Update user acccount information, if necessary
#     if first_name != captain[0]["first_name"]:
#         db.execute("""UPDATE accounts 
#                       SET first_name = ? 
#                       WHERE id = ?""", 
#                       first_name, session["user_id"])

#     if last_name != captain[0]["last_name"]:
#         db.execute("""UPDATE accounts 
#                       SET last_name = ? 
#                       WHERE id = ?""", 
#                       last_name, session["user_id"])

#     if phone_number != captain[0]["phone_number"]:
#         db.execute("""UPDATE accounts 
#                       SET phone_number = ? 
#                       WHERE id = ?""", 
#                       phone_number, session["user_id"])

#     if email != captain[0]["email"]:
#         db.execute("""UPDATE accounts 
#                       SET email = ? 
#                       WHERE id = ?""", 
#                       email, session["user_id"])

#     # Insert into teams database and update spots available
#     db.execute("""INSERT INTO teams (team_name, sponsor, event_id, passcode) 
#                   VALUES (?, ?, ?, ?)""", 
#                   team_name, sponsor, event_id, passcode)

#     db.execute("""UPDATE events 
#                   SET spots_available = spots_available - 1 
#                   WHERE id = ?""", 
#                   event_id)

#     # Add captain to registered_players
#     team_id = db.execute("""SELECT id 
#                             FROM teams 
#                             WHERE event_id = ? 
#                             AND team_name = ?""", 
#                             event_id, team_name)
#     db.execute("""INSERT INTO registered_players (captain, player_id, team_id, event_id) 
#                   VALUES (?, ?, ?, ?)""", 
#                   "Yes", session["user_id"], team_id[0]["id"], event_id)

#     flash("You have successfully registered your team. Your team passcode is %d. This passcode is also available in your profile." % (passcode), "success")
#     return redirect("/team_register")

# @app.route("/event_select", methods=["GET", "POST"])
# @login_required
# def event_select():
#     """Select an event before joining a team"""

#     # Select contact info from logged in user
#     player = db.execute("""SELECT email, first_name, last_name, phone_number 
#                            FROM accounts 
#                            WHERE id = ?""", 
#                            session["user_id"])

#     if request.method == "GET":
        
#         # Select events from events table
#         events = db.execute("SELECT * FROM events")

#         return render_template("event_selection.html", player=player, events=events)

#     # Get selected event
#     event = request.form.get("event")

#     if not event:
#         flash("Must select an event.", "error")
#         return redirect("/event_select")

#     if event:
#         event_id = db.execute("""SELECT id 
#                                  FROM events 
#                                  WHERE event_name = ?""", 
#                                  event)
            
#         # Select teams registered for selected event
#         teams = db.execute("""SELECT * 
#                               FROM teams 
#                               WHERE event_id = ?""", 
#                               event_id[0]["id"])

#     return render_template("player_register.html", player=player, event=event, teams=teams)
        

# @app.route("/player_register", methods=["GET", "POST"])
# @login_required
# def player_register():
#     """Join a team after selecting an event"""
   
#     # Select contact info from logged in user
#     player = db.execute("""SELECT email, first_name, last_name, phone_number 
#                            FROM accounts 
#                            WHERE id = ?""", 
#                            session["user_id"])

#     # User reached route via GET
#     if request.method == "GET":

#         event = request.args.get("event")

#         if event:
#             event_id = db.execute("""SELECT id 
#                                      FROM events 
#                                      WHERE event_name = ?""", 
#                                      event)
            
#             # Select teams registered for selected event
#             teams = db.execute("""SELECT * 
#                                   FROM teams 
#                                   WHERE event_id = ?""", 
#                                   event_id[0]["id"])

#         return render_template("player_register.html", event=event, player=player, teams=teams)

#     # User reached route via POST

#     # Validate form inputs
#     event = request.form.get("event")
#     team_id = int(request.form.get("team"))
#     first_name = request.form.get("firstname")
#     last_name = request.form.get("lastname")
#     phone_number = request.form.get("phonenumber")
#     email = request.form.get("email")
#     passcode = request.form.get("passcode")
#     captain = request.form.get("captain")

#     if not event:
#         flash("Must select an event.", "error")
#         return redirect("/event_select")

#     # Get event ID
#     event_id = db.execute("""SELECT id 
#                              FROM events 
#                              WHERE event_name = ?""", event)
#     print(event_id)
    
#     print(team_id)

#     if not team_id:
#         flash("Must select a team.", "error")
#         return redirect("/event_select")

#     # Get team ID
#     #team_id = db.execute("SELECT id FROM teams WHERE event_id = ? AND team_name = ?", event_id[0]["id"], team)

#     # Get team passcode
    
#     team_passcode = db.execute("""SELECT passcode 
#                                   FROM teams 
#                                   WHERE id = ?""", team_id)
#     team_passcode = int(team_passcode[0]["passcode"])
#     print(team_passcode)

#     if not first_name:
#         flash("Must enter a first name.", "error")
#         return redirect("/event_select")

#     if not last_name:
#         flash("Must enter a last name.", "error")
#         return redirect("/event_select")

#     if not phone_number:
#         flash("Must enter a phone number.", "error")
#         return redirect("/event_select")

#     if not phone_number.isdigit():
#         flash("Phone number must only contain numbers.", "error")
#         return redirect("/event_select")

#     if not email:
#         flash("Must enter an email.", "error")
#         return redirect("/event_select")

#     if not passcode:
#         flash("Must enter a passcode.", "error")
#         return redirect("/event_select")

#     if len(passcode) != 6:
#         flash("Passcode must be 6 digits", "error")
#         return redirect("/event_select")

#     passcode = int(passcode)

#     if passcode != team_passcode:
#         flash("Invalid passcode.", "error")
#         return redirect("/event_select")

#     # Check not already registered for event
#     if len(db.execute("""SELECT * 
#                          FROM registered_players 
#                          WHERE player_id = ? 
#                          AND event_id = ?""", 
#                          session["user_id"], event_id[0]["id"])) != 0:
#         flash("You are already registered for %s." % (event), "error")
#         return redirect("/event_select")

#     # Update account information, if necessary
#     if first_name != player[0]["first_name"]:
#         db.execute("""UPDATE accounts 
#                       SET first_name = ? 
#                       WHERE id = ?""", 
#                       first_name, session["user_id"])

#     if last_name != player[0]["last_name"]:
#         db.execute("""UPDATE accounts 
#                       SET last_name = ? 
#                       WHERE id = ?""", 
#                       last_name, session["user_id"])

#     if phone_number != player[0]["phone_number"]:
#         db.execute("""UPDATE accounts 
#                       SET phone_number = ?
#                       WHERE id = ?""", 
#                       phone_number, session["user_id"])

#     if email != player[0]["email"]:
#         db.execute("""UPDATE accounts 
#                       SET email = ? 
#                       WHERE id = ?""", 
#                       email, session["user_id"])

#     # Update registered_players
#     db.execute("""INSERT INTO registered_players (captain, player_id, team_id, event_id) 
#                   VALUES (?, ?, ?, ?)""", 
#                   captain, session["user_id"], team_id, event_id[0]["id"])

#     team_name = db.execute("""SELECT team_name 
#                               FROM teams WHERE id = ?""", 
#                               team_id)

#     flash("You have successfully registered for %s." % (team_name[0]["team_name"]), "success")
#     return redirect("/profile")

# @app.route("/leave_team", methods=["POST"])
# @login_required
# def leave_team():
#     """Leave team"""

#     team_id = int(request.form.get("leave"))

#     team_name = db.execute("""SELECT team_name 
#                               FROM teams 
#                               WHERE id = ?""", 
#                               team_id)

#     captain = db.execute("""SELECT captain 
#                             FROM registered_players 
#                             WHERE player_id = ? 
#                             AND team_id = ?""", 
#                             session["user_id"], team_id)

#     if captain[0]["captain"] == "Yes":
#         flash("Must designate alternative captain for %s before leaving team." % (team_name[0]["team_name"]), "error")
#         return redirect("/profile")

#     db.execute("""DELETE FROM registered_players 
#                   WHERE team_id = ? 
#                   AND player_id = ?""", 
#                   team_id, session["user_id"])

#     flash("You have successfully left %s." % (team_name[0]["team_name"]), "success")
#     return redirect("/profile")

# @app.route("/de-register_team", methods=["POST"])
# @login_required
# def deregister_team():
#     """De-Register Team"""

#     # Get selected team
#     team_id = int(request.form.get("de-register"))

#     # Get event id
#     event_id = db.execute("""SELECT event_id 
#                              FROM teams 
#                              WHERE id = ?""", 
#                              team_id)

#     # Get team name
#     team_name = db.execute("""SELECT team_name 
#                               FROM teams 
#                               WHERE id = ?""", 
#                               team_id)

#     # Delete team from teams table in database
#     db.execute("""DELETE FROM teams 
#                   WHERE id = ?""", 
#                   team_id)

#     # Delete team roster from registered_players table
#     db.execute("""DELETE FROM registered_players 
#                   WHERE team_id = ?""", 
#                   team_id)

#     # Update spots_available in events table
#     db.execute("""UPDATE events 
#                   SET spots_available = spots_available + 1 
#                   WHERE id = ?""", 
#                   event_id[0]["event_id"])

#     flash("You have successfully de-registered %s." % (team_name[0]["team_name"]), "success")
#     return redirect("/profile")

# @app.route("/update_captain", methods=["POST"])
# @login_required
# def update_captain():
#     """Update Captain"""

#     team_id = int(request.form.get("team_id"))

#     new_captain = int(request.form.get("new_captain"))

#     if not new_captain:
#         flash("Must select a new captain.", "error")
#         redirect("/profile")

#     # Get team name
#     team_name = db.execute("""SELECT team_name 
#                               FROM teams 
#                               WHERE id = ?""", 
#                               team_id)
    
#     # Update old captain in registered players table
#     db.execute("""UPDATE registered_players 
#                   SET captain = 'No' 
#                   WHERE player_id = ?
#                   AND team_id = ?""", 
#                   session["user_id"], team_id)

#     # Update new captain in registered players table
#     db.execute("""UPDATE registered_players 
#                   SET captain = 'Yes' 
#                   WHERE player_id = ?
#                   AND team_id = ?""", 
#                   new_captain, team_id)

#     flash("You have successfully updated the captain for %s." % (team_name[0]["team_name"]), "success")
#     return redirect("/profile")
