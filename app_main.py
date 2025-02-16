import sys
from PyQt6.QtWidgets import QApplication
from login_Window import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
