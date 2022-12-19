from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from random import randint


# Configure application
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kvkl_registration.db")

@app.route("/", methods=["GET"])
def index():
    """Generate homepage with list of events"""

    # Generate list of events
    events = db.execute("SELECT * FROM events")

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
    db.execute("INSERT INTO accounts (email, first_name, last_name, phone_number, password_hash, gender) VALUES (?, ?, ?, ?, ?, ?)", email, first_name, last_name, phone_number, generate_password_hash(password), gender)

    # Log new user in
    user = db.execute("SELECT id FROM accounts WHERE email = ?", email)
    session["user_id"] = user[0]["id"]

    flash("You have successfully created an account.", "success")
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

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
            flash("Invalid password", "error")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to homepage
    flash("You have successfully logged out", "success")
    return redirect("/")

@app.route("/team_register", methods=["GET", "POST"])
def team_register():
    """Register a new team"""

    # Select contact info from logged in user
    captain = db.execute("SELECT email, first_name, last_name, phone_number FROM accounts WHERE id = ?", session["user_id"])

    # User reached route via GET
    if request.method == "GET":
        
        # Select events from events table
        events = db.execute("SELECT * FROM events")
        
        return render_template("team_register.html", events=events, captain=captain)

    #User reached route via POST
    passcode = randint(100000, 999999)
    
    # Validate form inputs
    event = request.form.get("event")
    team_name = request.form.get("teamname")
    sponsor = request.form.get("sponsor")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    email = request.form.get("email")

    # Get event ID
    event_id = db.execute("SELECT id FROM events WHERE event_name = ?", event)

    if not event:
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

    if len(db.execute("SELECT team_name FROM teams WHERE team_name = ? AND event_id = ?", team_name, event_id[0]["id"])) != 0:
        flash("This team is already registered", "error")
        return redirect("/team_register")

    # Update user acccount information
    if first_name != captain[0]["first_name"]:
        db.execute("UPDATE accounts SET first_name = ? WHERE id = ?", first_name, session["user_id"])

    if last_name != captain[0]["last_name"]:
        db.execute("UPDATE accounts SET last_name = ? WHERE id = ?", last_name, session["user_id"])

    if phone_number != captain[0]["phone_number"]:
        db.execute("UPDATE accounts SET phone_number = ? WHERE id = ?", phone_number, session["user_id"])

    if email != captain[0]["email"]:
        db.execute("UPDATE accounts SET email = ? WHERE id = ?", email, session["user_id"])

    # Update account information, if necessary
    if first_name != captain[0]["first_name"]:
        db.execute("UPDATE accounts SET first_name = ? WHERE id = ?", first_name, session["user_id"])

    if last_name != captain[0]["last_name"]:
        db.execute("UPDATE accounts SET last_name = ? WHERE id = ?", last_name, session["user_id"])

    if phone_number != captain[0]["phone_number"]:
        db.execute("UPDATE accounts SET phone_number = ? WHERE id = ?", phone_number, session["user_id"])

    if email != captain[0]["email"]:
        db.execute("UPDATE accounts SET email = ? WHERE id = ?", email, session["user_id"])

    # Insert into teams database and update spots available
    db.execute("INSERT INTO teams (team_name, sponsor, event_id, captain_1, captain_2, passcode) VALUES (?, ?, ?, ?, ?, ?)", team_name, sponsor, event_id[0]["id"], captain[0]["first_name"], "N/A", passcode)

    db.execute("UPDATE events SET spots_available = spots_available - 1 WHERE id = ?", event_id[0]["id"])

    # Add captain to registered_players
    team_id = db.execute("SELECT id FROM teams WHERE event_id = ? AND team_name = ?", event_id[0]["id"], team_name)
    db.execute("INSERT INTO registered_players (captain, player_id, team_id) VALUES (?, ?, ?)", "Yes", session["user_id"], team_id[0]["id"])

    flash("You have successfully registered your team. Your team passcode is %d. This passcode will also be emailed to you" % (passcode), "success")
    return redirect("/team_register")

@app.route("/player_register", methods=["GET", "POST"])
def player_register():
    """Join a team"""

    # Select contact info from logged in user
    player = db.execute("SELECT email, first_name, last_name, phone_number FROM accounts WHERE id = ?", session["user_id"])

    # User reached route via GET
    if request.method == "GET":

        # Select events from events table
        events = db.execute("SELECT * FROM events")

        #render_template("player_register.html", events=events)

        # Get selected event from user
        #event = request.args.get("event")

        # Get event ID
        #event_id = db.execute("SELECT id FROM events WHERE event_name = ?", event)

        # Select teams registered for selected event
        #teams = db.execute("SELECT * FROM teams WHERE event_id = ?", event_id[0]["id"])

        return render_template("player_register.html", events=events, player=player)

    # User reached route via POST

    # Validate form inputs
    event = request.form.get("event")
    team = request.form.get("team")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    phone_number = request.form.get("phonenumber")
    email = request.form.get("email")
    passcode = int(request.form.get("passcode"))
    captain2 = request.form.get("captain")

    # Get event ID
    event_id = db.execute("SELECT id FROM events WHERE event_name = ?", event)

    # Get team ID
    team_id = db.execute("SELECT id FROM teams WHERE event_id = ? AND team_name = ?", event_id[0]["id"], team)

    # Get team passcode
    team_passcode = db.execute("SELECT passcode FROM teams WHERE id = ?", team_id[0]["id"])

    if not event:
        flash("Must select an event.", "error")
        return redirect("/player_register")

    if not team:
        flash("Must select a team.", "error")
        return redirect("/player_register")

    if not first_name:
        flash("Must enter a first name.", "error")
        return redirect("/player_register")

    if not last_name:
        flash("Must enter a last name.", "error")
        return redirect("/player_register")

    if not phone_number:
        flash("Must enter a phone number.", "error")
        return redirect("/player_register")

    if not phone_number.isdigit():
        flash("Phone number must only contain numbers.", "error")
        return redirect("/player_register")

    if not email:
        flash("Must enter an email.", "error")
        return redirect("/player_register")

    if not passcode:
        flash("Must enter a passcode.", "error")
        return redirect("/player_register")

    if passcode != team_passcode[0]["passcode"]:
        flash("Invalid passcode.", "error")
        return redirect("/player_register")

    # Update captain_2, if necessary
    if captain2 == "Yes":
        db.execute("UPDATE teams SET captain_2 = ? WHERE id = ?", first_name, team_id[0]["id"])

    # Update account information, if necessary
    if first_name != player[0]["first_name"]:
        db.execute("UPDATE accounts SET first_name = ? WHERE id = ?", first_name, session["user_id"])

    if last_name != player[0]["last_name"]:
        db.execute("UPDATE accounts SET last_name = ? WHERE id = ?", last_name, session["user_id"])

    if phone_number != player[0]["phone_number"]:
        db.execute("UPDATE accounts SET phone_number = ? WHERE id = ?", phone_number, session["user_id"])

    if email != player[0]["email"]:
        db.execute("UPDATE accounts SET email = ? WHERE id = ?", email, session["user_id"])

    # Update registered_players
    
@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Show user profile"""

    user = db.execute("SELECT * FROM accounts where id = ?", session["user_id"])

    history = db.execute("SELECT event_name, month, day, year, time, location, team_name, passcode, captain FROM events INNER JOIN teams ON events.id = teams.event_id INNER JOIN registered_players ON registered_players.team_id = teams.id WHERE registered_players.player_id = ? ORDER BY day ASC", session["user_id"])

    return render_template("profile.html", id=session["user_id"], user=user, history=history)

@app.route("/update", methods=["GET", "POST"])
def update():
    """Update account information"""

    # Get current user information
    user = db.execute("SELECT * FROM accounts where id = ?", session["user_id"])

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
        db.execute("UPDATE accounts SET first_name = ? WHERE id = ?", first_name, session["user_id"])

    if last_name != user[0]["last_name"]:
        db.execute("UPDATE accounts SET last_name = ? WHERE id = ?", last_name, session["user_id"])

    if phone_number != user[0]["phone_number"]:
        db.execute("UPDATE accounts SET phone_number = ? WHERE id = ?", phone_number, session["user_id"])

    if email != user[0]["email"]:
        db.execute("UPDATE accounts SET email = ? WHERE id = ?", email, session["user_id"])

    if gender != user[0]["gender"]:
        db.execute("UPDATE accounts SET gender = ? WHERE id = ?", gender, session["user_id"])

    flash("You have successfully updated your contact information.", "success")
    return redirect("/profile")