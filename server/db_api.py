import sqlite3

class DbApi:
    def __init__(self, db_path:str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='work';"
            content = cur.execute(query).fetchall()
            if content[0] != ("work",):
                query = "CREATE TABLE work (id INTEGER, pkey TEXT, work INTEGER, PRIMARY KEY(id,pkey));"
                cur.execute(query)
            conn.commit()

    def add_client(self,pkey):
        pass