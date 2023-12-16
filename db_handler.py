from cs50 import SQL

class DatabaseHandler:
    def __init__(self, database_uri):
        self.db = SQL(database_uri)

    # add methods for executing queries