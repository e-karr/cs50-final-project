from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kvkl_registration.db")

# Generate list of events
events = db.execute("SELECT * FROM events")

    # Get teams signed up for events
for event in events:
    event["teams"] = db.execute("SELECT team_name, id FROM teams where event_id = ?", event["id"])

for event in events:
    for team in event["teams"]:
        team["players"] = db.execute("SELECT first_name, last_name, captain FROM accounts INNER JOIN registered_players ON accounts.id = registered_players.player_id WHERE team_id = ?", team["id"])

for event in events:
    for team in event["teams"]:
        for player in team["players"]:
            print(player["first_name"], player["last_name"], player["captain"])



