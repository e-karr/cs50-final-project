from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kvkl_registration.db")

team_id = db.execute("SELECT id FROM teams WHERE event_id = 1 AND team_name = 'Hammond's Heroes'")

print(team_id)



