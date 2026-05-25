# Industrial Water Tank SCADA System

## 🏭 Overview
This project is an industrial-grade **SCADA (Supervisory Control and Data Acquisition)** application built in Python. It is designed to monitor a water tank's level, control a pump motor, manage alarms, and log historical data via Modbus TCP communication with an industrial PLC.

The application is built with a focus on thread-safety, fault-tolerance, and professional HMI (Human-Machine Interface) design.

---

## 🏗️ Architecture Diagram

```text
  [ Physical PLC / Hardware ] 
       ^              |
    (Modbus TCP IP Network)
       |              v
+---------------------------------------------------+
|               PYTHON SCADA BACKEND                |
|                                                   |
|  [ core/plc_comm.py ] (Hardware Interface)        |
|       ^             |                             |
|       |             v                             |
|  [ core/hardware.py ] (QThread Background Worker) |
|       |             |             |               |
|       v             v             v               |
|  [ alarms.py ] [ config.py ] [ database.py ]      |
+-------|---------------------------|---------------+
        | Signals/Slots             | SQL Queries
        v                           v
+---------------------------------------------------+
|               USER INTERFACE (HMI)                |
|                                                   |
|  [ core/gui.py ] (PySide6 Main Window)            |
|       |                                           |
|       +--> [ core/trends.py ] (Matplotlib Graph)  |
+---------------------------------------------------+
```

🧰 Core Components & Technologies Used

- **PySide6 (Qt for Python):**
  - Used for: The main Graphical User Interface (HMI).
  - Why: It is the industry standard for industrial displays. We utilize its QThread and Signal/Slot architecture to completely separate the UI from the hardware, ensuring the screen never freezes even if the network lags.
- **PyModbus:**
  - Used for: Network communication.
  - Why: Modbus TCP is the most widely used industrial protocol in the world. This allows the software to talk directly to standard PLCs (Siemens, Allen-Bradley, AutomationDirect, etc.).
- **SQLite3:**
  - Used for: The Industrial Historian (Database).
  - Why: Replaces fragile CSV files with a robust, serverless local database. It logs continuous sensor data and tracks every time the motor turns on/off. Includes an auto-pruning feature to prevent infinite file growth.
- **Pandas & Matplotlib:**
  - Used for: Historical Trend Graphing.
  - Why: Allows operators to visualize past tank levels based on real-time database queries, formatted with actual timestamps and shading.
- **JSON (Config System):**
  - Used for: External Configuration (`config.json`).
  - Why: Allows plant managers to change the PLC IP address, port, and Automatic Mode time schedules without altering the source code.

## ✨ Key Features

- **Dual Operation Modes:**
  - Manual: Direct operator control via UI buttons.
  - Automatic: Runs on a time-schedule defined in config.json (e.g., 5 PM to 6 PM).
- **Hardware Watchdog:** Software-level safety overrides automatically stop the pump if the tank reaches 100% capacity, preventing flooding.
- **Auto-Reconnect Logic:** If the 4G/GPRS router drops the connection, the software automatically detects the dead socket and attempts to reconnect.
- **Simulation Mode:** Can be run completely offline using simulated PLC data for testing and development.
- **Live Alarms:** Triggers and displays UI warnings for system anomalies (High Pressure, Low Flow).

## 📂 Project Structure

```text
PYTHON PROJECT/
│
├── industrial_project.py       # Main Entry Point (Run this file)
├── requirements.txt            # Python dependencies
├── config.json                 # Auto-generated settings file
├── scada.db                    # Auto-generated SQLite database
│
└── core/                       # Source Code
    ├── __init__.py             
    ├── gui.py                  # PySide6 UI Layout and styling
    ├── hardware.py             # Background QThread, logic, safety overrides
    ├── plc_comm.py             # PyModbus connection and reconnection logic
    ├── database.py             # SQLite table creation, insertion, and pruning
    ├── alarms.py               # Alarm trigger logic
    ├── config.py               # JSON reader/writer
    └── trends.py               # Matplotlib graph generation
```

## 🚀 How to Run

### Install Dependencies:
Ensure you are using a Python virtual environment, then install the required libraries:

```bash
pip install -r requirements.txt
```

(Requires: `PySide6`, `pymodbus`, `pandas`, `matplotlib`)

### Run the Application:
Always start the application from the root directory:

```bash
python industrial_project.py
```

### Configuration:
Upon first run, a `config.json` file will be generated. You can edit this file to switch `simulation_mode` to `false` and enter your real PLC's IP address.
