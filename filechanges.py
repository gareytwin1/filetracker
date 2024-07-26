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
    except BaseException as e:
        print(f"Error connecting to database: {e}")
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
    except sqlite3.Error as e:
        print(f"Error establishing cursor:{e}")
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
    except sqlite3.Error as e:
       print(f"Error connecting to database: {e}")
       conn.close()
    return result

def createhashtable(table):
    result = False
    query = f"""CREATE TABLE IF NOT EXISTS {table} (
             id Integer PRIMARY KEY,
             file_name text NOT NULL,
             hash_value text NOT NULL)"""
    try:
        conn = connectdb()
        if not conn is None:
            if not table_exists(table):
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                print(f"{table} table created in database!")
                conn.close()
                result = True
            else:
                # cursor.close()
                print(f"{table} table already in database.")
                conn.close()
    except sqlite3.Error as err:
        print(f"Error creating table: {err}")
    return result

        
def main():
    createhashtable("files")
    
    

if __name__ == "__main__":
    main()
    





