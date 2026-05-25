import sqlite3
from datetime import datetime

DB_NAME = "scada.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Auto-Migrate: If the database has "tank2_level", drop it to reset!
    cursor.execute("PRAGMA table_info(sensor_logs)")
    cols = [col[1] for col in cursor.fetchall()]
    if cols and "tank2_level" in cols:
        print("Reverting to Single Tank Database...")
        cursor.execute("DROP TABLE IF EXISTS sensor_logs")
        cursor.execute("DROP TABLE IF EXISTS device_logs")
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_logs 
                      (time TEXT, tank_level REAL, pressure REAL, flow REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS device_logs 
                      (device TEXT, start_time TEXT, stop_time TEXT, duration TEXT, trigger TEXT, start_level REAL, stop_level REAL)''')
    conn.commit()
    conn.close()
    prune_old_data(30)

def prune_old_data(days_to_keep):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM sensor_logs WHERE time <= datetime('now', 'localtime', '-{days_to_keep} days')")
        conn.commit()
        conn.close()
    except Exception: pass

def insert_sensor_data(tank_level, pressure, flow):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sensor_logs VALUES(?,?,?,?)", (current_time, tank_level, pressure, flow))
    conn.commit()
    conn.close()

def insert_device_log(device, start, stop, duration, trigger, start_lvl, stop_lvl):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO device_logs VALUES(?,?,?,?,?,?,?)", 
                   (device, start.strftime("%Y-%m-%d %H:%M:%S"), stop.strftime("%Y-%m-%d %H:%M:%S"), 
                    str(duration).split('.')[0], trigger, start_lvl, stop_lvl))
    conn.commit()
    conn.close()