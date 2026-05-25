def check_alarms(tank_level, pressure, flow):
    """Returns a list of active alarms based on current sensor data"""
    alarms = []
    if tank_level > 90:
        alarms.append("⚠️ HIGH TANK LEVEL (>90%)")
    if pressure > 10:
        alarms.append("⚠️ HIGH PRESSURE (>10 Bar)")
    if flow < 5:
        alarms.append("⚠️ LOW FLOW (<5 m3/hr)")
    return alarms