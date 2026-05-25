from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar, QMessageBox, QRadioButton, QGroupBox, QTextEdit)
from core.hardware import HardwareWorker
from core.trends import show_trend 
from core.config import load_config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Industrial SCADA - Single Tank, Dual Valves")
        self.setFixedSize(950, 450)

        main_layout = QHBoxLayout()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(main_layout)

        settings = load_config()
        in_start = str(settings.get("inlet_auto_start", "19:50"))
        in_stop = str(settings.get("inlet_auto_stop", "20:30"))
        out_start = str(settings.get("outlet_auto_start", "21:00"))
        out_stop = str(settings.get("outlet_auto_stop", "22:00"))

        # --- COL 1: TANK VISUAL ---
        tank_layout = QVBoxLayout()
        self.tank_bar = self.create_tank_bar("Main Water Tank")
        btn_trend = QPushButton("📊 Show Trends")
        btn_trend.setStyleSheet("background-color: #34495e; color: white; font-weight: bold; padding: 10px;")
        btn_trend.clicked.connect(show_trend)
        
        tank_layout.addWidget(QLabel("<b>Main Water Tank</b>"), alignment=Qt.AlignCenter)
        tank_layout.addWidget(self.tank_bar, alignment=Qt.AlignCenter)
        tank_layout.addWidget(btn_trend)

        # --- COL 2: INLET VALVE ---
        inlet_layout = QVBoxLayout()
        self.inlet_status = self.create_status_label("Inlet Valve: OFF")
        
        in_mode_box, self.in_rad_man, self.in_rad_auto = self.create_mode_box("Inlet Mode", f"Auto ({in_start}-{in_stop})")
        self.in_rad_man.toggled.connect(lambda: self.change_mode("INLET", self.in_rad_auto.isChecked()))
        
        self.in_btn_on, self.in_btn_off = self.create_buttons()
        self.in_btn_on.clicked.connect(lambda: self.hardware_worker._set_inlet(True, "MANUAL", self.tank_bar.value()))
        self.in_btn_off.clicked.connect(lambda: self.hardware_worker._set_inlet(False, "MANUAL", self.tank_bar.value()))

        inlet_layout.addWidget(QLabel("<b>Inlet Controls (Fill)</b>"), alignment=Qt.AlignCenter)
        inlet_layout.addWidget(in_mode_box)
        inlet_layout.addWidget(self.inlet_status)
        inlet_layout.addLayout(self.layout_buttons(self.in_btn_on, self.in_btn_off))
        inlet_layout.addStretch()

        # --- COL 3: OUTLET VALVE ---
        outlet_layout = QVBoxLayout()
        self.outlet_status = self.create_status_label("Outlet Valve: OFF")
        
        out_mode_box, self.out_rad_man, self.out_rad_auto = self.create_mode_box("Outlet Mode", f"Auto ({out_start}-{out_stop})")
        self.out_rad_man.toggled.connect(lambda: self.change_mode("OUTLET", self.out_rad_auto.isChecked()))
        
        self.out_btn_on, self.out_btn_off = self.create_buttons()
        self.out_btn_on.clicked.connect(lambda: self.hardware_worker._set_outlet(True, "MANUAL", self.tank_bar.value()))
        self.out_btn_off.clicked.connect(lambda: self.hardware_worker._set_outlet(False, "MANUAL", self.tank_bar.value()))

        outlet_layout.addWidget(QLabel("<b>Outlet Controls (Drain)</b>"), alignment=Qt.AlignCenter)
        outlet_layout.addWidget(out_mode_box)
        outlet_layout.addWidget(self.outlet_status)
        outlet_layout.addLayout(self.layout_buttons(self.out_btn_on, self.out_btn_off))
        outlet_layout.addStretch()

        # --- COL 4: ALARMS ---
        right_layout = QVBoxLayout()
        self.alarm_box = QTextEdit()
        self.alarm_box.setReadOnly(True)
        right_layout.addWidget(QLabel("<b>🚨 Active Alarms</b>"))
        right_layout.addWidget(self.alarm_box)

        main_layout.addLayout(tank_layout)
        main_layout.addSpacing(15)
        main_layout.addLayout(inlet_layout)
        main_layout.addSpacing(15)
        main_layout.addLayout(outlet_layout)
        main_layout.addSpacing(15)
        main_layout.addLayout(right_layout)

        # --- HARDWARE CONNECTIONS ---
        self.hardware_worker = HardwareWorker()
        self.hardware_worker.tank_signal.connect(self.tank_bar.setValue)
        self.hardware_worker.inlet_signal.connect(self.update_inlet_ui)
        self.hardware_worker.outlet_signal.connect(self.update_outlet_ui)
        self.hardware_worker.alarms_signal.connect(self.update_alarms)
        self.hardware_worker.error_signal.connect(self.show_error)
        self.hardware_worker.start()

    # --- GUI HELPERS ---
    def create_tank_bar(self, title):
        bar = QProgressBar()
        bar.setOrientation(Qt.Vertical)
        bar.setFixedSize(140, 250)
        bar.setTextVisible(True)
        bar.setAlignment(Qt.AlignCenter)
        bar.setStyleSheet("QProgressBar { border: 3px solid #7f8c8d; border-radius: 8px; background-color: #ecf0f1; color: black; font-size: 16px; font-weight: bold; } QProgressBar::chunk { background-color: #3498db; border-radius: 4px; }")
        return bar

    def create_status_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: red;")
        return lbl

    def create_mode_box(self, title, auto_text):
        box = QGroupBox(title)
        lyt = QVBoxLayout()
        rad_man = QRadioButton("Manual")
        rad_auto = QRadioButton(auto_text)
        rad_man.setChecked(True)
        lyt.addWidget(rad_man)
        lyt.addWidget(rad_auto)
        box.setLayout(lyt)
        return box, rad_man, rad_auto

    def create_buttons(self):
        on = QPushButton("ON")
        off = QPushButton("OFF")
        for b in (on, off): b.setMinimumHeight(45)
        on.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; font-weight: bold; } QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }")
        off.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-weight: bold; } QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }")
        return on, off

    def layout_buttons(self, b1, b2):
        l = QHBoxLayout()
        l.addWidget(b1)
        l.addWidget(b2)
        return l

    # --- SLOTS ---
    def change_mode(self, device, is_auto):
        if device == "INLET":
            self.hardware_worker.inlet_mode = "AUTO" if is_auto else "MANUAL"
            if is_auto: 
                self.in_btn_on.setEnabled(False)
                self.in_btn_off.setEnabled(False)
        else:
            self.hardware_worker.outlet_mode = "AUTO" if is_auto else "MANUAL"
            if is_auto: 
                self.out_btn_on.setEnabled(False)
                self.out_btn_off.setEnabled(False)

    @Slot(bool)
    def update_inlet_ui(self, is_on):
        if is_on:
            self.inlet_status.setText("Inlet Valve: ON")
            self.inlet_status.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")
            if self.hardware_worker.inlet_mode == "MANUAL":
                self.in_btn_on.setEnabled(False)
                self.in_btn_off.setEnabled(True)
        else:
            self.inlet_status.setText("Inlet Valve: OFF")
            self.inlet_status.setStyleSheet("font-size: 14px; font-weight: bold; color: red;")
            if self.hardware_worker.inlet_mode == "MANUAL":
                self.in_btn_on.setEnabled(True)
                self.in_btn_off.setEnabled(False)

    @Slot(bool)
    def update_outlet_ui(self, is_on):
        if is_on:
            self.outlet_status.setText("Outlet Valve: ON")
            self.outlet_status.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")
            if self.hardware_worker.outlet_mode == "MANUAL":
                self.out_btn_on.setEnabled(False)
                self.out_btn_off.setEnabled(True)
        else:
            self.outlet_status.setText("Outlet Valve: OFF")
            self.outlet_status.setStyleSheet("font-size: 14px; font-weight: bold; color: red;")
            if self.hardware_worker.outlet_mode == "MANUAL":
                self.out_btn_on.setEnabled(True)
                self.out_btn_off.setEnabled(False)

    @Slot(list)
    def update_alarms(self, alarms):
        self.alarm_box.clear()
        if not alarms:
            self.alarm_box.setStyleSheet("background-color: #e8f8f5; color: #27ae60; font-weight: bold;")
            self.alarm_box.append("✅ All Systems Normal")
        else:
            self.alarm_box.setStyleSheet("background-color: #fdfae3; color: #c0392b; font-weight: bold;")
            for a in alarms: self.alarm_box.append(a)

    @Slot(str)
    def show_error(self, message):
        QMessageBox.warning(self, "Hardware Warning", message)

    def closeEvent(self, event):
        self.hardware_worker.stop()
        event.accept()