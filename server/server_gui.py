import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, QObject
from server import ServerCore


class LogEmitter(QObject):
    log_signal = pyqtSignal(str)

class ServerThread(threading.Thread):
    def __init__(self, server_core, emitter):
        super().__init__(daemon=True)
        self.server_core = server_core
        self.emitter = emitter

    def run(self):
        
        original_print = print
        def custom_print(*args, **kwargs):
            message = ' '.join(map(str, args))
            self.emitter.log_signal.emit(message)
            original_print(*args, **kwargs)
        
        
        import builtins
        builtins.print = custom_print

        try:
            self.server_core.start()
        except Exception as e:
            self.emitter.log_signal.emit(f"[ERROR] {e}")
        finally:
            builtins.print = original_print

class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server GUI - File Transfer Analyzer")
        self.setGeometry(200, 200, 600, 400)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        self.start_button = QPushButton("Start Server")
        self.stop_button = QPushButton("Stop Server")
        self.stop_button.setEnabled(False)

        self.status_label = QLabel("Status: Stopped")

        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_box)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.server_core = ServerCore()
        self.emitter = LogEmitter()
        self.emitter.log_signal.connect(self.update_log)

        self.server_thread = None

        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)

    def start_server(self):
        self.server_thread = ServerThread(self.server_core, self.emitter)
        self.server_thread.start()
        self.status_label.setText("Status: Running")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_server(self):
        self.server_core.stop()
        self.status_label.setText("Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_log("Server stopped by user.")

    def update_log(self, message):
        self.log_box.append(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerWindow()
    window.show()
    sys.exit(app.exec_())
