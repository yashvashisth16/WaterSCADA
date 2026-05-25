import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "plc_ip": "192.168.1.10",
    "plc_port": 502,
    "simulation_mode": True,
    "inlet_auto_start": "19:50",
    "inlet_auto_stop": "20:30",
    "outlet_auto_start": "21:00",
    "outlet_auto_stop": "22:00"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as file:
            json.dump(DEFAULT_CONFIG, file, indent=4)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except:
        return DEFAULT_CONFIG