from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kvkl_registration.db")

teams = db.execute("SELECT event_name, team_name FROM events INNER JOIN teams ON events.id=teams.event_id GROUP BY events.id")

passcode = db.execute("SELECT team_name, passcode FROM teams")

print(passcode)

print(teams)

