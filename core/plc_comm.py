from pymodbus.client import ModbusTcpClient
import random 
from core.config import load_config 

settings = load_config()
PLC_IP = settings.get("plc_ip", "192.168.1.10")
PLC_PORT = settings.get("plc_port", 502)
SIMULATION_MODE = settings.get("simulation_mode", True)

client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

def connect_plc():
    if SIMULATION_MODE: return True
    return client.connect()

def ensure_connection():
    if SIMULATION_MODE: return True
    if not client.is_socket_open(): return client.connect()
    return True

def read_plc_data(sim_tank, sim_inlet, sim_outlet):
    if SIMULATION_MODE:
        return {
            "tank_level": sim_tank,
            "pressure": random.uniform(8.0, 11.5), 
            "flow": random.uniform(3.0, 15.0),     
            "inlet_status": 1 if sim_inlet else 0,
            "outlet_status": 1 if sim_outlet else 0
        }
    
    if not ensure_connection(): return None
    
    try:
        # THE FIX: We simply removed "slave=1". The newest pymodbus handles it automatically!
        result = client.read_holding_registers(address=0, count=5)
        
        if result.isError(): return None
        
        return {
            "tank_level": result.registers[0],
            "pressure": result.registers[1],
            "flow": result.registers[2],
            "inlet_status": result.registers[3],
            "outlet_status": result.registers[4]
        }
    except Exception as e:
        print(f"Modbus Read Drop: {e}")
        client.close() # Reset the connection so it can retry safely
        return None

def write_inlet_state(state):
    if SIMULATION_MODE: return True
    if not ensure_connection(): return False
    try:
        # THE FIX: Removed "slave=1"
        return not client.write_coil(address=0, value=state).isError()
    except:
        client.close()
        return False

def write_outlet_state(state):
    if SIMULATION_MODE: return True
    if not ensure_connection(): return False
    try:
        # THE FIX: Removed "slave=1"
        return not client.write_coil(address=1, value=state).isError()
    except:
        client.close()
        return False

def close_plc():
    client.close()