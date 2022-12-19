from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///kvkl_registration.db")

events = db.execute("SELECT * FROM events")

teams = {}

for event in events:
    event_name = db.execute("SELECT event_name FROM events WHERE id = ?", event["id"])
    teams["event_name"] = db.execute("SELECT team_name FROM teams WHERE event_id = ?", event["id"])
    #team_list = db.execute("SELECT events.id, team_name FROM teams INNER JOIN events ON teams.event_id = events.id WHERE event_id = ?", event["id"])
    #teams.append(team_list)


print(teams)

# [[{'id': 1, 'team_name': "Hammond's Heroes"}], 
# [{'id': 2, 'team_name': 'Kansas Tree Care'}, {'id': 2, 'team_name': 'Harbour Lights'}], 
# [{'id': 3, 'team_name': 'Rainbow Unicorns'}, {'id': 3, 'team_name': 'Finance Bros'}]]

