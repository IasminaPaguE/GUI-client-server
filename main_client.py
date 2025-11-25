
from PyQt5.QtWidgets import QApplication
from client.client_view import ClientWindow
from client.client_controller import ClientController
from client.client_core import ClientCore
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientWindow()
    client_core = ClientCore()
    controller = ClientController(window, client_core)
    window.show()
    sys.exit(app.exec_())