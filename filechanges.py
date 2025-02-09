import os
import sys
import hashlib
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

def table_exists(table='files'):
    """Checks if a SQLite DB Table exists"""
    result = False
    conn = connectdb()
    try:
        if conn is not None:
            query = """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name=?
            """
            args = (table,)
            result = corecursor(conn, query, args)
    except sqlite3.Error as e:
        print(f"Error finding if table exists: {e}")
    finally:
        if conn:
            conn.close()
    return result

def create_hash_table(table='files'):
    result = False
    query = f"""CREATE TABLE IF NOT EXISTS {table} (
             id Integer PRIMARY KEY,
             file_name text NOT NULL,
             hash_value text NOT NULL)"""
    conn = connectdb()
    try:
        if not conn is None:
            if not table_exists(table):
                cursor = conn.cursor()
                try:
                    cursor.execute(query)
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"Error executing query while creating hash table: {e}")
                result = True
    except sqlite3.Error as e:
        print(f"Error creating hash table: {e}")
    finally:
        if conn:
            conn.close()
    return result

def create_hash_table_idx(table='files', index_name='idxfile'):
    query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} (file_name)"
    conn = connectdb()
    try:
        if conn is not None:
            if table_exists(table):
                try:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"Error executing query while creating hash table index: {e}")
    except sqlite3.Error as e:
        print(f"Error creating hash table index: {e}")
    finally:
        if conn:
            conn.close()

"""Run a specific command on the SQLite DB"""
def runcmd(qry, args, table='files'):
    conn = connectdb()
    try:
        if not conn is None:
            if table_exists(table):
                try:
                    cursor = conn.cursor()
                    cursor.execute(qry, args)
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
    runcmd(qry, args)

"""Insert into the SQLite Files Table"""
def insert_hash_table(fname, md5, table='files'):
    qry = f"INSERT INTO {table} (file_name, hash_value) VALUES (?, ?)"
    args = (fname, md5)
    runcmd(qry, args)

"""Setup the Hash Table"""
def setup_hash_table(fname, md5, table='files'):
    create_hash_table()
    create_hash_table_idx()
    insert_hash_table(fname, md5)

"""Checks if the md5 has tag exists in the SQLite DB"""
def md5indb(fname, table='files'):
    items = []
    qry = f"SELECT hash_value FROM {table} WHERE file_name = ?"
    args = (fname,)
    conn = connectdb()
    try:
        if not conn is None:
            if table_exists(table):
                cursor = conn.cursor()
                try:
                    cursor.execute(qry, args)
                    rows = cursor.fetchall()
                    for row in rows:
                        if row[0] is not None:
                            items.append(row[0])
                except sqlite3.Error as e:
                    print(f"Error executing query finding md5 hash: {e}")
    except sqlite3.Error as e:
        print(f"Error executing query md5 hash: {e}")
    finally:
        if conn:
            conn.close()
    return items

def print_all_tables():
    conn = connectdb()
    try:
        if not conn is None:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if tables:
                print("Tables in the database:", end=' ')
                for table in tables:
                    print(table[0])
            else:
                print("No tables found in the database.")
    except sqlite3.Error as e:
        print(f"Error retrieving tables: {e}")
    finally:
        if conn:
            conn.close()

def print_table_columns(table='files'):
    conn = connectdb()
    try:
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

def haschanged(fname, md5):
    """Check if the file has changed"""
    result = False
    old_md5 = md5indb(fname)
    numitems = len(old_md5)
    if numitems > 0:
        if md5 != old_md5[0]:
            result = True
            update_hash_table(fname, md5)
    else:
        setup_hash_table(fname, md5)
    return result

def getfileext(fname):
    """Get the file extension"""
    return os.path.splitext(fname)[1]

def getmoddate(fname):
    """Get the file modification date"""
    try:
        return os.path.getmtime(fname)
    except OSError as e:
        print(f"Error getting file modification date: {e}")
        return None

def md5short(fname):
    """Get md5 file hash tag using the hashlib.md5 function
       UTF-8 encoding must be used to encode the file data"""
    return hashlib.md5(str(fname + '|' + str(getmoddate(fname))).encode('utf-8')).hexdigest()

def runfilechages(ws): # ws is the worksheet??
    # Invoke the function that loads and parses the config file
    flds, exts = loadflds()
    for i, fld in enumerate(flds):
        changed = checkfilechanges(fld, exts, ws)
    return changed

    
def loadflds():
    # Load the fields from the config file
    flds = []
    exts = []
    config =  getbasefile() + '.ini'
    if os.path.isfile(config):
        with open(config, 'r') as f:
            for line in f:
                flds.append(line.split('|')[0].strip())
                exts.append(line.split('|')[1].strip()) # need to strip the commas, not correct
    return flds, exts

def checkfilechanges(folder, exclude, ws):
    changed = False
    """Check for file changes"""
    for subdir, dirs, files in os.walk(folder):
        for fname in files:
            if fname not in exclude:
                fname = os.path.join(subdir, fname)
                if os.path.isfile(fname):
                    md5 = md5short(fname)
                    if haschanged(fname, md5):
                        print(f"File {fname} has changed!") # -> Log the file change to Excel report
                        changed = True
    return changed

def main():
    """Testing the functions created"""
    table = 'files'
    if create_hash_table():
        print(f"{table} table created in database!")
    else:
        print(f"{table} table already in database.")

    create_hash_table_idx()
    print_all_tables()
    print_table_columns()
    print(md5short('filechanges.py'))

if __name__ == "__main__":
    main()
    





