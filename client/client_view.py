from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QTextEdit, QFileDialog, QVBoxLayout, QWidget

class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client GUI - File Transfer Analyzer")
        self.setGeometry(200, 200, 600, 400)

        self.select_button = QPushButton("Select File/Directory")
        self.send_button = QPushButton("Send to Server")
        self.send_button.setEnabled(False)
        self.status_label = QLabel("Status: Idle")
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.select_button)
        layout.addWidget(self.send_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_box)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
