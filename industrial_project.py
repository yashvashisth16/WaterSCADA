import sys
from PySide6.QtWidgets import QApplication

# Import the GUI from your core folder
from core.gui import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Keep the application running until closed
    sys.exit(app.exec())

if __name__ == "__main__":
    main()