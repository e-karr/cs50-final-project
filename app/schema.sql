DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS registered_players;

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone_number NUMERIC NOT NULL,
    password_hash TEXT NOT NULL,
    gender TEXT NOT NULL
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    event_name TEXT NOT NULL,
    month TEXT NOT NULL,
    day INTEGER NOT NULL,
    year INTEGER NOT NULL,
    time TEXT NOT NULL,
    location TEXT NOT NULL,
    number_teams INTEGER NOT NULL,
    spots_available INTEGER NOT NULL
);

CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    team_name TEXT NOT NULL,
    sponsor TEXT,
    event_id INTEGER NOT NULL,
    passcode INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE registered_players(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    captain TEXT NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    FOREIGN KEY (player_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

INSERT INTO events (event_name, month, day, year, time, location, number_teams, spots_available)
VALUES ('2024 Season', 'May', 19, 2024, '5:00pm', 'YSC', 36, 36);

INSERT INTO events (event_name, month, day, year, time, location, number_teams, spots_available)
VALUES ('Spring Charity Tournament', 'April', 28, 2024, '12:00pm', 'Holcom Park', 16, 16);

INSERT INTO events (event_name, month, day, year, time, location, number_teams, spots_available)
VALUES ('Yard Games', 'July', 13, 2024, '12:00pm', 'Broken Arrow Park', 20, 20);
