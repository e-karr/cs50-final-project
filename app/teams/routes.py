from app.teams import bp
from flask import (
    flash, g, redirect, render_template, request, url_for,
)
from random import randint
from app.auth.routes import login_required
from app.extensions import db
from app.models.event import Event
from app.models.account import Account
from app.models.team import Team
from app.models.player import Player

@bp.route("/team_register", methods=("GET", "POST"))
@login_required
def team_register():
    """Register a new team"""

    user = g.user

    # User reached route via GET
    if request.method == "GET":
        events = Event.query.all()
        return render_template("team/team_register.html", events=events, user=user)

    #User reached route via POST

    # Generate random 6-digit passcode
    passcode = randint(100000, 999999)
    event_id = request.form.get("event")
    team_name = request.form.get("teamname")
    sponsor = request.form.get("sponsor")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    email = request.form.get("email")
    error = None

    if event_id:
        event_id = int(event_id)
        existing_team = Team.query.filter_by(team_name=team_name, event_id=event_id).first()
        selected_event = Event.query.filter_by(id=event_id).first()
        already_registered = Player.query.filter_by(player_id=user.id, event_id=event_id).first()

    # Validate form inputs
    if not event_id:
        error = "Must select an event."
    elif not team_name:
        error = "Must enter a team name."
    elif not first_name:
        error = "Must enter a first name."
    elif not last_name:
        error = "Must enter a last name."
    elif not phone_number:
        error = "Must enter a phone number."
    elif not email:
        error = "Must enter an email."
    elif existing_team:
        error = f"This team is already registered for {selected_event.event_name}"
    elif already_registered:
        error = f"You are already registered for {selected_event.event_name}"
    else:
        error = Account.validate_phone_number(phone_number)

    if error == None:
        try:
            # Update account information, if necessary
            if first_name != user.first_name:
                user.update_first_name(first_name, db.session)

            if last_name != user.last_name:
                user.update_last_name(last_name, db.session)

            if phone_number != user.phone_number:
                user.update_phone_number(phone_number, db.session)

            if email != user.email:
                user.update_email(email, db.session)

            # Insert into teams database
            team = Team(
                team_name=team_name,
                sponsor=sponsor,
                event_id=event_id,
                passcode=passcode
            )
            db.session.add(team)
            db.session.commit()

            # update spots available
            selected_event.update_spots_available(db.session)

            # Add captain to registered_players
            player = Player(
                captain="Yes",
                player_id=user.id,
                team_id=team.id,
                event_id=event_id
            )
            db.session.add(player)
            db.session.commit()
            
            flash(f"You have successfully registered your team. Your team passcode is {passcode}.", "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            print(f"Error: {e}")
            error = "An error occured while registering a team."
            db.session.rollback()

    flash(error, 'error')
    return redirect(url_for('teams.team_register'))

@bp.route("/event_select", methods=("GET", "POST"))
@login_required
def event_select():
    return "Pending updates"
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
        

@bp.route("/player_register", methods=("GET", "POST"))
@login_required
def player_register():
    return "Pending updates"
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

@bp.route("/leave_team", methods=["POST"])
@login_required
def leave_team():
    return "Pending updates"
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

@bp.route("/de-register_team", methods=["POST"])
@login_required
def deregister_team():
    return "Pending updates"
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

@bp.route("/update_captain", methods=["POST"])
@login_required
def update_captain():
    return "Pending updates"
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