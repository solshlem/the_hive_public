import sqlite3

def init_db():
    conn = sqlite3.connect('cases.db')
    cursor = conn.cursor()

    migration = open('migration1.sql', 'r').read()
    cursor.execute(migration)
    conn.commit()
    
    conn.close()

def get_slave_id_from_db(case_id):
    conn = sqlite3.connect('cases.db')
    cursor = conn.cursor()

    cursor.execute('SELECT slave_id FROM cases WHERE id = ?', (case_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

    conn.close()

def add_new_case(master_id, city):
    conn = sqlite3.connect('cases.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO cases (master_id, city) VALUES (?, ?)', (master_id, city))
    conn.commit()
    conn.close()

def get_case_by_master_id(master_id):
    conn = sqlite3.connect('cases.db')
    cursor = conn.cursor()

    cursor.execute('SELECT slave_id FROM cases WHERE master_id = ?', (master_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else result

def update_case_slave_id(master_id, slave_id):
    conn = sqlite3.connect('cases.db')
    c = conn.cursor()

    try:
        c.execute("UPDATE cases SET slave_id = ? WHERE master_id = ?", (slave_id, master_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating case slave_id: {e}")
    finally:
        conn.close()
        