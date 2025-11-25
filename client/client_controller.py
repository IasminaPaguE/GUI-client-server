from PyQt5.QtWidgets import QFileDialog
from client.client_view import ClientWindow
from client.client_core import ClientCore

class ClientController:
    def __init__(self, window: ClientWindow, client_core: ClientCore):
        self.window = window
        self.client_core = client_core
        self.selected_path = None

        self.window.select_button.clicked.connect(self.select_file_or_directory)
        self.window.send_button.clicked.connect(self.send_to_server)

    def select_file_or_directory(self):
        path, _ = QFileDialog.getOpenFileName(self.window, "Select File")
        if path:
            self.selected_path = path
            self.window.status_label.setText(f"Selected: {path}")
            self.window.send_button.setEnabled(True)

    def send_to_server(self):
        if self.selected_path:
            self.window.status_label.setText("Sending...")
            # Call client_core to send file
            self.client_core.send_file(self.selected_path)
            self.window.status_label.setText("Sent!")
