from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import login_required
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from random import randint
from functools import wraps
import os

from db_handler import DatabaseHandler
from user_handler import UserHandler
from team_handler import TeamHandler
from event_handler import EventHandler


def create_app():
    # Configure application
    app = Flask(__name__)

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kvkl_registration.db")

db_handler = DatabaseHandler("sqlite:///kvkl_registration.db")
user_handler = UserHandler(db_handler)
team_handler = TeamHandler(db_handler)
event_handler = EventHandler(db_handler)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET"])
def index():
    """Generate homepage with list of events"""

    # Generate list of events
    events = db.execute("SELECT * FROM events")

    # Get teams signed up for events
    for event in events:
        event["teams"] = db.execute("""SELECT team_name, id, sponsor 
                                        FROM teams where event_id = ?""", 
                                        event["id"])

    for event in events:
        for team in event["teams"]:
            team["players"] = db.execute("""SELECT first_name, last_name, accounts.id, captain 
                                            FROM accounts 
                                            INNER JOIN registered_players 
                                            ON accounts.id = registered_players.player_id 
                                            WHERE team_id = ?""", 
                                            team["id"])

    # Show homepage
    return render_template("index.html", events=events)

@app.route("/account", methods=["GET", "POST"])
def account():
    """Create a new account"""
    
    # show create an account page
    if request.method == "GET":
        return render_template("account.html")

    # get input from create account form
    email = request.form.get("email")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    gender = request.form.get("gender")

    special_characters = ['$', '#', '@', '!', '*']

    # Validate first name
    if not first_name:
        flash("Must enter first name", "error")
        return redirect("/account")

    # Validate last name
    if not last_name:
        flash("Must enter last name", "error")
        return redirect("/account")

    # Validate phone number
    if not phone_number:
        flash("Must enter phone number", "error")
        return redirect("/account")

    if not phone_number.isdigit():
        flash("Phone number must only contain numbers.", "error")
        return redirect("/account")
    
    # Validate email
    if not email:
        flash("Must enter an email.", "error")
        return redirect("/account")

    if len(db.execute("SELECT email FROM accounts WHERE email = ?", email)) != 0:
        flash("Account already exists using this email", "error")
        return redirect("/account")

    # Validate password - Password must contain at least 8 characters, 1 capital letter, 1 number, and 1 special character.
    if not password:
        flash("Must enter a password.", "error")
        return redirect("/account")

    if not confirmation:
        flash("Must confirm password.", "error")
        return redirect("/account")

    if password != confirmation:
        flash("Passwords don't match.", "error")
        return redirect("/account")

    if len(password) < 8:
        flash("Password must be at least 8 characters.", "error")
        return redirect("/account")

    if not any(i.isdigit() for i in password):
        flash("Password must contain at least one number.", "error")
        return redirect("/account")

    if not any(j.isupper() for j in password):
        flash("Password must contain at least one capital letter.", "error")
        return redirect("/account")

    if not any(k in special_characters for k in password):
        flash("Password must contain at least one special character ($, #, @, !, *).", "error")
        return redirect("/account")

    # Validate gender
    if not gender:
        flash("Must select a gender", "error")
        return redirect("/account")
    
    # Remember new account
    db.execute("""INSERT INTO accounts (email, first_name, last_name, phone_number, password_hash, gender) 
                  VALUES (?, ?, ?, ?, ?, ?)""", 
                  email, first_name, last_name, phone_number, generate_password_hash(password), gender)

    # Log new user in
    user = db.execute("SELECT id FROM accounts WHERE email = ?", email)
    session["user_id"] = user[0]["id"]

    flash("You have successfully created an account.", "success")
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST
    if request.method == "POST": 

        # Get input values
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Check that email was entered
        if not email:
            flash("Please enter an email.", "error")
            return redirect("/login")

        # Check that password was entered
        if not password:
            flash("Please enter a password.", "error")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM accounts WHERE email = ?", email)

        # Check for valid email
        if len(rows) != 1:
            flash("Invalid email", "error")
            return redirect("/login")

        if not check_password_hash(rows[0]["password_hash"], password):
            flash("Invalid password.", "error")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to homepage
    flash("You have successfully logged out.", "success")
    return redirect("/")

@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():

    captain = db.execute("""SELECT captain, team_name 
                            FROM registered_players 
                            INNER JOIN teams ON teams.id = registered_players.team_id 
                            WHERE player_id = ?""", 
                            session["user_id"])

    for i in captain:
        if i["captain"] == "Yes":
            flash("Must designate alternative captain for %s before deleting account." % (i["team_name"]), "error")
            return redirect("/profile")

    db.execute("DELETE FROM accounts WHERE id = ?", session["user_id"])

    flash("Your account was successfully deleted.", "success")
    session.clear()
    return redirect("/")

@app.route("/team_register", methods=["GET", "POST"])
@login_required
def team_register():
    """Register a new team"""

    # Select contact info from logged in user
    captain = db.execute("""SELECT email, first_name, last_name, phone_number 
                            FROM accounts WHERE id = ?""", 
                            session["user_id"])

    # User reached route via GET
    if request.method == "GET":
        
        # Select events from events table
        events = db.execute("SELECT * FROM events")
        
        return render_template("team_register.html", events=events, captain=captain)

    #User reached route via POST

    # Generate random 6-digit passcode
    passcode = randint(100000, 999999)
    
    # Validate form inputs
    event_id = int(request.form.get("event"))
    team_name = request.form.get("teamname")
    sponsor = request.form.get("sponsor")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    email = request.form.get("email")

    if not event_id:
        flash("Must select an event.", "error")
        return redirect("/team_register")

    if not team_name:
        flash("Must enter a team name.", "error")
        return redirect("/team_register")

    if not first_name:
        flash("Must enter a first name.", "error")
        return redirect("/team_register")

    if not last_name:
        flash("Must enter a last name.", "error")
        return redirect("/team_register")

    if not phone_number:
        flash("Must enter a phone number.", "error")
        return redirect("/team_register")

    if not phone_number.isdigit():
        flash("Phone number must only contain numbers.", "error")
        return redirect("/team_register")

    if not email:
        flash("Must enter an email.", "error")
        return redirect("/team_register")

    if len(db.execute("""SELECT team_name 
                         FROM teams 
                         WHERE team_name = ? 
                         AND event_id = ?""", 
                         team_name, event_id)) != 0:
        flash("This team is already registered", "error")
        return redirect("/team_register")

    # Check that player isn't already registered for event
    event_name = db.execute("SELECT event_name FROM events WHERE id = ?", event_id)
    if len(db.execute("""SELECT * 
                         FROM registered_players 
                         WHERE player_id = ? 
                         AND event_id = ?""", 
                         session["user_id"], event_id)) != 0:
        flash("You are already registered for %s." % (event_name[0])["event_name"], "error")
        return redirect("/team_register")

    # Update user acccount information, if necessary
    if first_name != captain[0]["first_name"]:
        db.execute("""UPDATE accounts 
                      SET first_name = ? 
                      WHERE id = ?""", 
                      first_name, session["user_id"])

    if last_name != captain[0]["last_name"]:
        db.execute("""UPDATE accounts 
                      SET last_name = ? 
                      WHERE id = ?""", 
                      last_name, session["user_id"])

    if phone_number != captain[0]["phone_number"]:
        db.execute("""UPDATE accounts 
                      SET phone_number = ? 
                      WHERE id = ?""", 
                      phone_number, session["user_id"])

    if email != captain[0]["email"]:
        db.execute("""UPDATE accounts 
                      SET email = ? 
                      WHERE id = ?""", 
                      email, session["user_id"])

    # Insert into teams database and update spots available
    db.execute("""INSERT INTO teams (team_name, sponsor, event_id, passcode) 
                  VALUES (?, ?, ?, ?)""", 
                  team_name, sponsor, event_id, passcode)

    db.execute("""UPDATE events 
                  SET spots_available = spots_available - 1 
                  WHERE id = ?""", 
                  event_id)

    # Add captain to registered_players
    team_id = db.execute("""SELECT id 
                            FROM teams 
                            WHERE event_id = ? 
                            AND team_name = ?""", 
                            event_id, team_name)
    db.execute("""INSERT INTO registered_players (captain, player_id, team_id, event_id) 
                  VALUES (?, ?, ?, ?)""", 
                  "Yes", session["user_id"], team_id[0]["id"], event_id)

    flash("You have successfully registered your team. Your team passcode is %d. This passcode is also available in your profile." % (passcode), "success")
    return redirect("/team_register")

@app.route("/event_select", methods=["GET", "POST"])
@login_required
def event_select():
    """Select an event before joining a team"""

    # Select contact info from logged in user
    player = db.execute("""SELECT email, first_name, last_name, phone_number 
                           FROM accounts 
                           WHERE id = ?""", 
                           session["user_id"])

    if request.method == "GET":
        
        # Select events from events table
        events = db.execute("SELECT * FROM events")

        return render_template("event_selection.html", player=player, events=events)

    # Get selected event
    event = request.form.get("event")

    if not event:
        flash("Must select an event.", "error")
        return redirect("/event_select")

    if event:
        event_id = db.execute("""SELECT id 
                                 FROM events 
                                 WHERE event_name = ?""", 
                                 event)
            
        # Select teams registered for selected event
        teams = db.execute("""SELECT * 
                              FROM teams 
                              WHERE event_id = ?""", 
                              event_id[0]["id"])

    return render_template("player_register.html", player=player, event=event, teams=teams)
        

@app.route("/player_register", methods=["GET", "POST"])
@login_required
def player_register():
    """Join a team after selecting an event"""
   
    # Select contact info from logged in user
    player = db.execute("""SELECT email, first_name, last_name, phone_number 
                           FROM accounts 
                           WHERE id = ?""", 
                           session["user_id"])

    # User reached route via GET
    if request.method == "GET":

        event = request.args.get("event")

        if event:
            event_id = db.execute("""SELECT id 
                                     FROM events 
                                     WHERE event_name = ?""", 
                                     event)
            
            # Select teams registered for selected event
            teams = db.execute("""SELECT * 
                                  FROM teams 
                                  WHERE event_id = ?""", 
                                  event_id[0]["id"])

        return render_template("player_register.html", event=event, player=player, teams=teams)

    # User reached route via POST

    # Validate form inputs
    event = request.form.get("event")
    team_id = int(request.form.get("team"))
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    email = request.form.get("email")
    passcode = request.form.get("passcode")
    captain = request.form.get("captain")

    if not event:
        flash("Must select an event.", "error")
        return redirect("/event_select")

    # Get event ID
    event_id = db.execute("""SELECT id 
                             FROM events 
                             WHERE event_name = ?""", event)
    print(event_id)
    
    print(team_id)

    if not team_id:
        flash("Must select a team.", "error")
        return redirect("/event_select")

    # Get team ID
    #team_id = db.execute("SELECT id FROM teams WHERE event_id = ? AND team_name = ?", event_id[0]["id"], team)

    # Get team passcode
    
    team_passcode = db.execute("""SELECT passcode 
                                  FROM teams 
                                  WHERE id = ?""", team_id)
    team_passcode = int(team_passcode[0]["passcode"])
    print(team_passcode)

    if not first_name:
        flash("Must enter a first name.", "error")
        return redirect("/event_select")

    if not last_name:
        flash("Must enter a last name.", "error")
        return redirect("/event_select")

    if not phone_number:
        flash("Must enter a phone number.", "error")
        return redirect("/event_select")

    if not phone_number.isdigit():
        flash("Phone number must only contain numbers.", "error")
        return redirect("/event_select")

    if not email:
        flash("Must enter an email.", "error")
        return redirect("/event_select")

    if not passcode:
        flash("Must enter a passcode.", "error")
        return redirect("/event_select")

    if len(passcode) != 6:
        flash("Passcode must be 6 digits", "error")
        return redirect("/event_select")

    passcode = int(passcode)

    if passcode != team_passcode:
        flash("Invalid passcode.", "error")
        return redirect("/event_select")

    # Check not already registered for event
    if len(db.execute("""SELECT * 
                         FROM registered_players 
                         WHERE player_id = ? 
                         AND event_id = ?""", 
                         session["user_id"], event_id[0]["id"])) != 0:
        flash("You are already registered for %s." % (event), "error")
        return redirect("/event_select")

    # Update account information, if necessary
    if first_name != player[0]["first_name"]:
        db.execute("""UPDATE accounts 
                      SET first_name = ? 
                      WHERE id = ?""", 
                      first_name, session["user_id"])

    if last_name != player[0]["last_name"]:
        db.execute("""UPDATE accounts 
                      SET last_name = ? 
                      WHERE id = ?""", 
                      last_name, session["user_id"])

    if phone_number != player[0]["phone_number"]:
        db.execute("""UPDATE accounts 
                      SET phone_number = ?
                      WHERE id = ?""", 
                      phone_number, session["user_id"])

    if email != player[0]["email"]:
        db.execute("""UPDATE accounts 
                      SET email = ? 
                      WHERE id = ?""", 
                      email, session["user_id"])

    # Update registered_players
    db.execute("""INSERT INTO registered_players (captain, player_id, team_id, event_id) 
                  VALUES (?, ?, ?, ?)""", 
                  captain, session["user_id"], team_id, event_id[0]["id"])

    team_name = db.execute("""SELECT team_name 
                              FROM teams WHERE id = ?""", 
                              team_id)

    flash("You have successfully registered for %s." % (team_name[0]["team_name"]), "success")
    return redirect("/profile")
    
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show user profile"""

    # get user information from accounts table
    user = db.execute("""SELECT * 
                         FROM accounts 
                         WHERE id = ?""", 
                         session["user_id"])

    # get registration history
    history = db.execute("""SELECT event_name, 
                                   month, 
                                   day, 
                                   year, 
                                   time, 
                                   location, 
                                   team_name, 
                                   passcode, 
                                   captain, 
                                   teams.id 
                            FROM events 
                            INNER JOIN teams 
                                ON events.id = teams.event_id 
                                INNER JOIN registered_players 
                                    ON registered_players.team_id = teams.id 
                                    WHERE registered_players.player_id = ?""", 
                            session["user_id"])

    # get team rosters
    for team in history:
        team["players"] = db.execute("""SELECT first_name, last_name, captain, accounts.id 
                                        FROM accounts 
                                        INNER JOIN registered_players 
                                            ON accounts.id = registered_players.player_id 
                                            WHERE team_id = ?""", 
                                        team["id"])

    return render_template("profile.html", id=session["user_id"], user=user, history=history)

@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Update account information"""

    # Get current user information
    user = db.execute("""SELECT * 
                         FROM accounts 
                         WHERE id = ?""", 
                        session["user_id"])

    # User reaches page via GET
    if request.method == "GET":
        return render_template("update.html", user=user)

    # User reaches page via POST

    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    email = request.form.get("email")
    gender = request.form.get("gender")

    # Update account information, if necessary
    if first_name != user[0]["first_name"]:
        db.execute("""UPDATE accounts 
                      SET first_name = ? 
                      WHERE id = ?""", 
                    first_name, session["user_id"])

    if last_name != user[0]["last_name"]:
        db.execute("""UPDATE accounts 
                      SET last_name = ? 
                      WHERE id = ?""", 
                    last_name, session["user_id"])

    if phone_number != user[0]["phone_number"]:
        db.execute("""UPDATE accounts 
                      SET phone_number = ? 
                      WHERE id = ?""", 
                      phone_number, session["user_id"])

    if email != user[0]["email"]:
        db.execute("""UPDATE accounts 
                      SET email = ? 
                      WHERE id = ?""", 
                      email, session["user_id"])

    if gender != user[0]["gender"]:
        db.execute("""UPDATE accounts 
                      SET gender = ? 
                      WHERE id = ?""", 
                      gender, session["user_id"])

    flash("You have successfully updated your contact information.", "success")
    return redirect("/profile")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change Password"""

    # User reaches page via GET
    if request.method == "GET":
        return render_template("password.html")

    # User reaches page via POST
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirmation = request.form.get("confirmation")

    old_hash = db.execute("""SELECT password_hash 
                             FROM accounts WHERE id = ?""", 
                             session["user_id"])

    special_characters = ['$', '#', '@', '!', '*']

    if not old_password:
        flash("Must enter current password.", "error")
        return redirect("/password")

    if not new_password:
        flash("Must enter new password.", "error")
        return redirect("/password")

    if not confirmation:
        flash("Must confirm new password.", "error")
        return redirect("/password")

    # Validate password inputs
    if not check_password_hash(old_hash[0]["password_hash"], old_password):
        flash("Invalid current password.", "error")
        return redirect("/password")

    if new_password != confirmation:
        flash("New passwords don't match.", "error")
        return redirect("/password")

    if len(new_password) < 8:
        flash("Password must be at least 8 characters.", "error")
        return redirect("/password")

    if not any(i.isdigit() for i in new_password):
        flash("Password must contain at least one number.", "error")
        return redirect("/password")

    if not any(j.isupper() for j in new_password):
        flash("Password must contain at least one capital letter.", "error")
        return redirect("/password")

    if not any(k in special_characters for k in new_password):
        flash("Password must contain at least one special character ($, #, @, !, *).", "error")
        return redirect("/password")

    db.execute("""UPDATE accounts 
                  SET password_hash = ? 
                  WHERE id = ?""", 
                  generate_password_hash(new_password), session["user_id"])

    flash("Your password has been successfully updated.", "success")
    return redirect("/profile")

@app.route("/leave_team", methods=["POST"])
@login_required
def leave_team():
    """Leave team"""

    team_id = int(request.form.get("leave"))

    team_name = db.execute("""SELECT team_name 
                              FROM teams 
                              WHERE id = ?""", 
                              team_id)

    captain = db.execute("""SELECT captain 
                            FROM registered_players 
                            WHERE player_id = ? 
                            AND team_id = ?""", 
                            session["user_id"], team_id)

    if captain[0]["captain"] == "Yes":
        flash("Must designate alternative captain for %s before leaving team." % (team_name[0]["team_name"]), "error")
        return redirect("/profile")

    db.execute("""DELETE FROM registered_players 
                  WHERE team_id = ? 
                  AND player_id = ?""", 
                  team_id, session["user_id"])

    flash("You have successfully left %s." % (team_name[0]["team_name"]), "success")
    return redirect("/profile")

@app.route("/de-register_team", methods=["POST"])
@login_required
def deregister_team():
    """De-Register Team"""

    # Get selected team
    team_id = int(request.form.get("de-register"))

    # Get event id
    event_id = db.execute("""SELECT event_id 
                             FROM teams 
                             WHERE id = ?""", 
                             team_id)

    # Get team name
    team_name = db.execute("""SELECT team_name 
                              FROM teams 
                              WHERE id = ?""", 
                              team_id)

    # Delete team from teams table in database
    db.execute("""DELETE FROM teams 
                  WHERE id = ?""", 
                  team_id)

    # Delete team roster from registered_players table
    db.execute("""DELETE FROM registered_players 
                  WHERE team_id = ?""", 
                  team_id)

    # Update spots_available in events table
    db.execute("""UPDATE events 
                  SET spots_available = spots_available + 1 
                  WHERE id = ?""", 
                  event_id[0]["event_id"])

    flash("You have successfully de-registered %s." % (team_name[0]["team_name"]), "success")
    return redirect("/profile")

@app.route("/update_captain", methods=["POST"])
@login_required
def update_captain():
    """Update Captain"""

    team_id = int(request.form.get("team_id"))

    new_captain = int(request.form.get("new_captain"))

    if not new_captain:
        flash("Must select a new captain.", "error")
        redirect("/profile")

    # Get team name
    team_name = db.execute("""SELECT team_name 
                              FROM teams 
                              WHERE id = ?""", 
                              team_id)
    
    # Update old captain in registered players table
    db.execute("""UPDATE registered_players 
                  SET captain = 'No' 
                  WHERE player_id = ?
                  AND team_id = ?""", 
                  session["user_id"], team_id)

    # Update new captain in registered players table
    db.execute("""UPDATE registered_players 
                  SET captain = 'Yes' 
                  WHERE player_id = ?
                  AND team_id = ?""", 
                  new_captain, team_id)

    flash("You have successfully updated the captain for %s." % (team_name[0]["team_name"]), "success")
    return redirect("/profile")
