import sys
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QLabel,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QGridLayout,
)
from PyQt5.QtCore import pyqtSignal, QObject
from server.server_controller import ServerController
import pyqtgraph as pg


class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server GUI - File Transfer Analyzer")
        self.setGeometry(200, 200, 900, 600)

        # --- Controller ---
        self.controller = ServerController()

        # --- UI ---
        self._setup_ui()

        self.throughput_data = []
        self.cpu_data = []
        self.ram_data = []
        self.sample_index = 0 

        # --- Signals ---
        self.controller.realtime_signal.connect(self.update_realtime_charts)
        self.controller.metrics_signal.connect(self.update_final_metrics)

    # ==========================
    # UI setup
    # ==========================
    def _setup_ui(self):
        self.start_button = QPushButton("Start Server")
        self.stop_button = QPushButton("Stop Server")
        self.stop_button.setEnabled(False)

        self.status_label = QLabel("Status: Stopped")
        self.tabs = QTabWidget()

        # TAB 1: Logs
        logs_tab = QWidget()
        logs_layout = QVBoxLayout()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        logs_layout.addWidget(self.log_box)
        logs_tab.setLayout(logs_layout)

        # TAB 2: Metrics + Charts
        metrics_tab = QWidget()
        metrics_layout = QVBoxLayout()

        #QTextEdit for final metrics
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setPlaceholderText("Transfer metrics will appear here after a file is received.")
        metrics_layout.addWidget(self.metrics_text)

        # Charts area
        charts_grid = QGridLayout()

        # Throughput plot
        self.throughput_plot = pg.PlotWidget()
        self.throughput_plot.setTitle("Throughput (MB/s)")
        self.throughput_plot.setLabel("left", "MB/s")
        self.throughput_plot.setLabel("bottom", "Sample")
        self.throughput_curve = self.throughput_plot.plot([])

        # CPU plot
        self.cpu_plot = pg.PlotWidget()
        self.cpu_plot.setTitle("CPU Usage (%)")
        self.cpu_plot.setLabel("left", "%")
        self.cpu_plot.setLabel("bottom", "Sample")
        self.cpu_curve = self.cpu_plot.plot([])

        # RAM plot
        self.ram_plot = pg.PlotWidget()
        self.ram_plot.setTitle("RAM Usage (%)")
        self.ram_plot.setLabel("left", "%")
        self.ram_plot.setLabel("bottom", "Sample")
        self.ram_curve = self.ram_plot.plot([])

        charts_grid.addWidget(self.throughput_plot, 0, 0)
        charts_grid.addWidget(self.cpu_plot, 0, 1)
        charts_grid.addWidget(self.ram_plot, 1, 0, 1, 2)

        charts_container = QWidget()
        charts_container.setLayout(charts_grid)

        metrics_layout.addWidget(charts_container)

        metrics_tab.setLayout(metrics_layout)

        #adding tabs to main tab widget
        self.tabs.addTab(logs_tab, "Logs")
        self.tabs.addTab(metrics_tab, "Metrics & Charts")

        # main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.stop_button)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # button actions
        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)

    # ==========================
    # Server control
    # ==========================

    def start_server(self):
        # reset charts data when starting or restarting the server
        self.reset_charts()
        self.controller.start_server()
        self.status_label.setText("Status: Running")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.update_log("[INFO] Server started.")


    def stop_server(self):
        self.controller.stop_server()
        self.status_label.setText("Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_log("[INFO] Server stopped by user.")

    # ==========================
    # Log update
    # ==========================
    def update_log(self, message: str):
        self.log_box.append(message)

    # ==========================
    # Metrics & Charts
    # ==========================
    def reset_charts(self):
        self.throughput_data = []
        self.cpu_data = []
        self.ram_data = []
        self.sample_index = 0

        self.throughput_curve.setData([])
        self.cpu_curve.setData([])
        self.ram_curve.setData([])

    def update_realtime_charts(self, throughput: float, cpu: float, ram: float):
        self.throughput_data.append(throughput)
        self.cpu_data.append(cpu)
        self.ram_data.append(ram)
        self.sample_index += 1

        x = list(range(len(self.throughput_data)))

        
        self.throughput_curve.setData(x, self.throughput_data)
        self.cpu_curve.setData(x, self.cpu_data)
        self.ram_curve.setData(x, self.ram_data)

    def update_final_metrics(self, metrics: dict):
        
        text_lines = [
            f"File name: {metrics.get('file_name')}",
            f"File size: {metrics.get('file_size')} bytes",
            f"File type: {metrics.get('file_type')}",
            "",
            f"Total transfer time: {metrics.get('total_transfer_time'):.4f} s",
            f"Avg throughput: {metrics.get('throughput'):.4f} MB/s",
            f"Peak throughput: {metrics.get('peak_throughput'):.4f} MB/s",
            f"Transfer byte difference: {metrics.get('transfer_byte_difference')}",
            f"Transfer status: {metrics.get('transfer_status')}",
            "",
            f"CPU avg: {metrics.get('cpu_usage_avg'):.2f} %",
            f"CPU peak: {metrics.get('cpu_usage_peak'):.2f} %",
            f"RAM avg: {metrics.get('ram_usage_avg'):.2f} %",
            f"RAM peak: {metrics.get('ram_usage_peak'):.2f} %",
        ]
        self.metrics_text.setPlainText("\n".join(text_lines))


