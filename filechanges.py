import os
import sqlite3

def getbasefile():
    """Name of the SQLite DB file"""
    return os.path.splitext(os.path.basename(__file__))[0]

def connectdb():
    """Connect to the SQLite DB"""
    try:
        db_file = getbasefile() + '.db'
        conn = sqlite3.connect(db_file)
    except BaseException as err:
        print(f"Error connecting to database: {err}")
        conn = None
    return conn

def corecursor(conn, query, args):
    """Opens a SQLite DB cursor"""
    result = False
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        rows = cursor.fetchall()
        numrows = len(list(rows))
        if numrows > 0:
            result = True
    except sqlite3.Error as err:
        print(f"Error establishing cursor:{err}")
        if cursor != None:
            conn.close()
    return result


def table_exists(table):
    """Checks if a SQLite DB Table exists"""
    result = False
    try:
        conn = connectdb()
        if not conn is None:
           query = """
           SELECT name
           FROM sqlite_master
           WHERE type='table' AND name=?
           """
           args = (table,)
           result = corecursor(conn, query, args)
           conn.close()
    except sqlite3.Error as err:
       print(f"Error connecting to database: {err}")
       conn.close()
    return result

def main():
    if table_exists("files"):
        print(f"Table already exists")
    else:
        print(f"Table does not exists.")
    

if __name__ == "__main__":
    main()
    





