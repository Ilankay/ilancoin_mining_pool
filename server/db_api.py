import sqlite3
from exceptions import ClientExists
class DbApi:
    def __init__(self, db_path:str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='work';"
            content = cur.execute(query).fetchall()
            if ("work",) not in content:
                query = "CREATE TABLE work (id INTEGER PRIMARY KEY, waddr BLOB, work INTEGER);"
                cur.execute(query)
            conn.commit()

    def add_client(self,waddr):
        query = "SELECT * FROM work WHERE waddr = ?;"
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(query,waddr)
            if len(cur.fetchall()) != 0: raise ClientExists
            query = "INSERT INTO work (waddr, work) VALUES (?,0)"
            cur.execute(query,waddr)
            conn.commit()
            return
 