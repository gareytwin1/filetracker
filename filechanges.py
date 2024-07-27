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
    except sqlite3.Error as e:
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
    finally:    
        if cursor:
            cursor.close()
    return result

def table_exists(table):
    """Checks if a SQLite DB Table exists"""
    result = False
    try:
        conn = connectdb()
        if conn is not None:
            query = """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name=?
            """
            args = (table,)
            result = corecursor(conn, query, args)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    finally:
        if conn:
            conn.close()
    return result

def create_hash_table(table):
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
                result = True
    except sqlite3.Error as e:
        print(f"Error creating hash table: {e}")
    finally:
        if conn:
            conn.close()
    return result

def create_hash_table_idx(table='files', index_name='idxfile'):
    query = f'CREATE INDEX IF NOT EXISTS {index_name} ON {table} (file_name)'
    try:    
        conn = connectdb()
        if conn is not None:
            if table_exists(table):
                try:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"Error creating hash table index: {e}")
    except sqlite3.Error as e:
        print(f"Error creating hash table index: {e}")
    finally:
        if conn:
            conn.close()

"""Run a specific command on the SQLite DB"""
def runcmd(qry, table):
    try:
        conn = connectdb()
        if not conn is None:
            if table_exists(table):
                try:
                    cursor = conn.cursor()
                    cursor.execute(qry)
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"Error running query: {e}")
    except sqlite3.Error as e:
        print(f"Error running query: {e}")
    finally:
        if conn:
            conn.close()

"""Update the SQLite File Table"""
def update_hash_table(fname, md5, table='files'):
    qry = f"UPDATE {table} SET hash_value = ? WHERE file_name = ?"
    args = (md5, fname)
    runcmd(qry, table)

"""Insert into the SQLite Files Table"""
def insert_hash_table(fname, md5, table='files'):
    qry = f"INSERT INTO {table} (file_name, hash_value) VALUES (?, ?)"
    args = (fname, md5)
    runcmd(qry, table)

"""Setup the Hash Table"""
def setup_hash_table(fname, md5, table='files'):
    create_hash_table(table)
    create_hash_table_idx(table)
    insert_hash_table(fname, md5, table)

"""Checks if the md5 has tag exists in the SQLite DB"""
def md5indb(fname, table='files'):
    items = []
    qry = "SELECT hash_value FROM {table} WHERE file_name = ?"
    args = (fname,)
    try:
        conn = connectdb()
        if not conn is None:
            if table_exists(table):
                try:
                    cursor = conn.cursor()
                    cursor.execute(qry, args)
                    items = cursor.fetchall()
                    for item in items:
                        if item[0] is not None:
                            items.append(item[0])
                except sqlite3.Error as e:
                    print(f"Error executing query finding md5 hash: {e}")
    except sqlite3.Error as e:
        print(f"Error executing query md5 hash: {e}")
    finally:
        if conn:
            conn.close()
    return items

def print_all_tables():
    try:
        conn = connectdb()
        if not conn is None:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if tables:
                print("Tables in the database:")
                for table in tables:
                    print(table[0])
            else:
                print("No tables found in the database.")
    except sqlite3.Error as e:
        print(f"Error retrieving tables: {e}")
    finally:
        if conn:
            conn.close()

def print_table_columns(table):
    try:
        conn = connectdb()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            if columns:
                print(f"Columns in the '{table}' table:")
                for column in columns:
                    print(f"Column ID: {column[0]}, Name: {column[1]}, Type: {column[2]}")
            else:
                print(f"No columns found for table '{table}'.")
    except sqlite3.Error as e:
        print(f"Error retrieving columns: {e}")
    finally:
        if conn:
            conn.close()

def main():
    table = 'files'
    if create_hash_table(table):
        print(f"{table} table created in database!")
    else:
        print(f"{table} table already in database.")

    create_hash_table_idx()
    print_all_tables()
    print_table_columns(table)

if __name__ == "__main__":
    main()
    





