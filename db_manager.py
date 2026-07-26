import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('helicor.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Tabla de proyectos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            hpn TEXT PRIMARY KEY,
            name TEXT,
            customer TEXT,
            owner TEXT,
            city TEXT,
            state TEXT,
            region TEXT,
            start_date TEXT,
            end_date TEXT,
            round_piles REAL,
            square_piles REAL,
            total_revenue REAL,
            labor REAL,
            transportation REAL,
            machinery REAL,
            other_exp REAL
        )
    ''')
    
    # Tabla de registros diarios (avances y notas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hpn TEXT,
            piles_added REAL,
            log_date TEXT,
            note TEXT,
            user_author TEXT,
            image_path TEXT
        )
    ''')
    
    # NUEVA TABLA: Para guardar los pagos de los tranches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tranche_payments (
            hpn TEXT,
            tranche_label TEXT,
            is_paid INTEGER,
            PRIMARY KEY (hpn, tranche_label)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_projects():
    conn = sqlite3.connect('helicor.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM projects", conn)
    conn.close()
    return df

def add_project(data):
    conn = sqlite3.connect('helicor.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', data)
    conn.commit()
    conn.close()

def get_daily_logs(hpn):
    conn = sqlite3.connect('helicor.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM daily_logs WHERE hpn = ?", conn, params=(hpn,))
    conn.close()
    return df

def add_daily_log(hpn, piles_added, log_date, note, user_author, image_path):
    conn = sqlite3.connect('helicor.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO daily_logs (hpn, piles_added, log_date, note, user_author, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (hpn, piles_added, log_date, note, user_author, image_path))
    conn.commit()
    conn.close()

# NUEVAS FUNCIONES DE PAGOS DE TRANCHES
def save_tranche_payment(hpn, label, is_paid):
    conn = sqlite3.connect('helicor.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO tranche_payments (hpn, tranche_label, is_paid)
        VALUES (?, ?, ?)
    ''', (hpn, label, 1 if is_paid else 0))
    conn.commit()
    conn.close()

def get_tranche_payments(hpn):
    conn = sqlite3.connect('helicor.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT tranche_label, is_paid FROM tranche_payments WHERE hpn = ?", (hpn,))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: bool(row[1]) for row in rows}