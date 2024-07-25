import sqlite3


def connect_db():
    conn = sqlite3.connect("datafile.db")
    return conn

def corecursor(conn, query, args):
    cursor = conn.cursor()
    cursor.execute(query, args)
    return cursor.fetchone()

def table_exists(conn, table_name):
    """Checks if a SQLite DB Table exists"""
    result = False
    try:
        conn = connect_db()
        if not conn is None:
           # cursor = conn.cursor()
           query = f"""
           SELECT name
           FROM sqlite_master
           WHERE type='table' AND name=?
           """
           args = (table_name,)
           result = corecursor(conn, query, args)
           return result is not None
    except sqlite3.Error as e:
       print("Error connecting to database: {e}")

connection = connect_db()

if connection:
    table_name = 'files'
    if table_exists(connection, table_name):
        print(f"Table {table_name} already exists")
    else:
        print(f"Table {table_name} does not exists.")
        connection.close()
else:
    print("Failed to establish connection")






