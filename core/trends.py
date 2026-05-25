import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates 

def show_trend():
    try:
        conn = sqlite3.connect("scada.db")
        df = pd.read_sql("SELECT * FROM sensor_logs", conn)
        conn.close()

        if df.empty: return

        df['time'] = pd.to_datetime(df['time'])

        plt.figure("Historical Data", figsize=(8, 5))
        plt.clf() 
        
        plt.plot(df['time'], df['tank_level'], label="Water Level", color='#2980b9', linewidth=2)
        plt.fill_between(df['time'], df['tank_level'], color='#3498db', alpha=0.3)

        plt.title("Tank Level Trend", fontsize=14, fontweight='bold')
        plt.xlabel("Real Time", fontsize=12)
        plt.ylabel("Water Level (%)", fontsize=12)
        
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()

        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.gcf().autofmt_xdate() 
        plt.tight_layout() 
        plt.show(block=False) 
        
    except Exception as e:
        print(f"Error loading trends: {e}")