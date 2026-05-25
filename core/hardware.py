import time
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from core import plc_comm, database, alarms
from core.config import load_config 

class HardwareWorker(QThread):
    tank_signal = Signal(int)
    inlet_signal = Signal(bool)
    outlet_signal = Signal(bool)
    alarms_signal = Signal(list) 
    error_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True
        settings = load_config()
        self.inlet_auto_start = str(settings.get("inlet_auto_start", "19:50"))
        self.inlet_auto_stop = str(settings.get("inlet_auto_stop", "20:30"))
        self.outlet_auto_start = str(settings.get("outlet_auto_start", "21:00"))
        self.outlet_auto_stop = str(settings.get("outlet_auto_stop", "22:00"))

        self.inlet_mode = "MANUAL"
        self.outlet_mode = "MANUAL"
        
        self.inlet_start_time, self.inlet_trigger, self.inlet_start_level = None, None, 0
        self.outlet_start_time, self.outlet_trigger, self.outlet_start_level = None, None, 0

        self.sim_inlet_on = False
        self.sim_outlet_on = False
        self.sim_tank = 10 

        database.init_db()

    def run(self):
        if not plc_comm.connect_plc(): self.error_signal.emit("Could not connect to PLC!")

        while self.is_running:
            try:
                # 1. SIMULATION MATH 
                if self.sim_inlet_on: self.sim_tank += 5
                if self.sim_outlet_on: self.sim_tank -= 5
                self.sim_tank = max(0, min(100, self.sim_tank))

                # 2. READ PLC
                data = plc_comm.read_plc_data(self.sim_tank, self.sim_inlet_on, self.sim_outlet_on)
                
                if data:
                    tank = data["tank_level"]
                    inlet_on = bool(data["inlet_status"])
                    outlet_on = bool(data["outlet_status"])

                    database.insert_sensor_data(tank, data["pressure"], data["flow"])
                    self.alarms_signal.emit(alarms.check_alarms(tank, data["pressure"], data["flow"]))

                    now = datetime.now().time()
                    
                    # 3. INLET AUTO
                    if self.inlet_mode == "AUTO":
                        start = datetime.strptime(self.inlet_auto_start, "%H:%M").time()
                        stop = datetime.strptime(self.inlet_auto_stop, "%H:%M").time()
                        if start <= now < stop and not inlet_on and tank < 100:
                            self._set_inlet(True, "AUTOMATIC", tank)
                        elif inlet_on and self.inlet_trigger == "AUTOMATIC":
                            self._set_inlet(False, "AUTOMATIC", tank)

                    # 4. OUTLET AUTO
                    if self.outlet_mode == "AUTO":
                        start = datetime.strptime(self.outlet_auto_start, "%H:%M").time()
                        stop = datetime.strptime(self.outlet_auto_stop, "%H:%M").time()
                        if start <= now < stop and not outlet_on and tank > 0:
                            self._set_outlet(True, "AUTOMATIC", tank)
                        elif outlet_on and self.outlet_trigger == "AUTOMATIC":
                            self._set_outlet(False, "AUTOMATIC", tank)

                    # 5. SAFETY OVERRIDES
                    if tank >= 100 and inlet_on:
                        self._set_inlet(False, "SAFETY_OVERRIDE", tank)
                        self.error_signal.emit("Tank Full! Inlet Valve auto-shutoff.")
                    if tank <= 0 and outlet_on:
                        self._set_outlet(False, "SAFETY_OVERRIDE", tank)
                        self.error_signal.emit("Tank Empty! Outlet Valve auto-shutoff.")

                    # 6. UPDATE GUI
                    self.tank_signal.emit(tank)
                    self.inlet_signal.emit(inlet_on)
                    self.outlet_signal.emit(outlet_on)

            except Exception as e:
                self.error_signal.emit(f"Hardware Loop Error: {str(e)}")
            time.sleep(2.0) 

    def _set_inlet(self, turn_on, trigger, current_level):
        if turn_on:
            if plc_comm.write_inlet_state(True):
                self.sim_inlet_on, self.inlet_trigger = True, trigger
                self.inlet_start_time, self.inlet_start_level = datetime.now(), current_level
        else:
            if plc_comm.write_inlet_state(False):
                self.sim_inlet_on = False
                if self.inlet_start_time:
                    dur = datetime.now() - self.inlet_start_time
                    database.insert_device_log("Inlet Valve", self.inlet_start_time, datetime.now(), dur, self.inlet_trigger, self.inlet_start_level, current_level)
                    self.inlet_start_time = None

    def _set_outlet(self, turn_on, trigger, current_level):
        if turn_on:
            if plc_comm.write_outlet_state(True):
                self.sim_outlet_on, self.outlet_trigger = True, trigger
                self.outlet_start_time, self.outlet_start_level = datetime.now(), current_level
        else:
            if plc_comm.write_outlet_state(False):
                self.sim_outlet_on = False
                if self.outlet_start_time:
                    dur = datetime.now() - self.outlet_start_time
                    database.insert_device_log("Outlet Valve", self.outlet_start_time, datetime.now(), dur, self.outlet_trigger, self.outlet_start_level, current_level)
                    self.outlet_start_time = None

    def stop(self):
        self.is_running = False
        self._set_inlet(False, "SHUTDOWN", self.sim_tank)
        self._set_outlet(False, "SHUTDOWN", self.sim_tank)
        plc_comm.close_plc()
        self.wait()