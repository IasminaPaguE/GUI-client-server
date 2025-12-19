import sys
from PyQt5.QtWidgets import QApplication
from server.server_gui import ServerWindow
from dotenv import load_dotenv


if not load_dotenv() :
    print("No .env file found or failed to load")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerWindow()
    window.show()
    sys.exit(app.exec_())
