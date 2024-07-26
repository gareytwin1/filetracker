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

def create_hash_table(table):
    result = False
    query = f"""CREATE TABLE IF NOT EXISTS {table} (
             id Integer PRIMARY KEY,
             file_name text NOT NULL,
             hash_value text NOT NULL,
             file_size Integer NOT NULL)"""
    try:
        conn = connectdb()
        if not conn is None:
            if not table_exists(table):
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
                conn.close()
                result = True
            else:
                # cursor.close()
                conn.close()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    return result

def create_hash_table_idx():
    table = 'files'
    index_name = 'idxfile'
    query = f'CREATE INDEX IF NOT EXISTS {index_name} ON {table} (file_name)'
    try:    
        conn = connectdb()
        if conn is not None:
            if table_exists(table):
                try:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                    cursor.close()
                    print(f"Index '{index_name}' created successfully.")
                    return True
                except sqlite3.Error as err:
                    print(f"Error creating index: {err}")
            else:
                print(f"Index '{index_name}' already exists.")
        else:
            print(f"Table '{table}' does not exist.")
    except sqlite3.Error as err:
        print(f"Error: {err}")
    finally:
        if conn:
            conn.close()
            
def print_all_tables():
    try:
        conn = connectdb()
        if not conn is None:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
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
            cursor.close()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error retrieving columns: {e}")

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
    





