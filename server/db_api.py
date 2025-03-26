import sqlite3
from exceptions import ClientExists


class DbApi:
    def __init__(self, db_path:str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='work';"
            cur.execute(query)
            content = cur.fetchall()
            if ("work",) not in content:
                query = "CREATE TABLE work (id INTEGER PRIMARY KEY, waddr TEXT, work INTEGER);"
                cur.execute(query)
            conn.commit()

    def add_client(self,waddr):
        query = "SELECT * FROM work WHERE waddr = ?;"
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(query,(waddr,))
            if len(cur.fetchall()) != 0: raise ClientExists
            query = "INSERT INTO work (waddr, work) VALUES (?,1)"
            cur.execute(query,(waddr,))
            conn.commit()
            return

    def list_addresses_work(self):
        query = "SELECT JSON_GROUP_ARRAY(JSON_ARRAY(waddr, work)) AS result FROM work;"
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(query)
            return cur.fetchall()[0][0]

    def add_work(self,waddr):
        query = "UPDATE your_table SET work = work + 1 WHERE waddr = ?;"
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(query,(waddr,))
            conn.commit()
        return

if __name__ == "__main__":
    db = DbApi("work.db")
    try:
        db.add_client("kasldfjj12314")
        db.add_client("123fdfw123")
    except ClientExists:
        pass
    print(db.list_addresses_work())
