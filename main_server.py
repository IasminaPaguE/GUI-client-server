
import sys
from PyQt5.QtWidgets import QApplication
from server.server_gui import ServerWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerWindow()
    window.show()
    sys.exit(app.exec_())
