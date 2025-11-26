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

from server import ServerCore

import pyqtgraph as pg


class LogEmitter(QObject):
    log_signal = pyqtSignal(str)


class MetricsEmitter(QObject):
    # dict cu metrics finale (to_dict() din FileTransferMetrics)
    metrics_signal = pyqtSignal(dict)
    # throughput(MB/s), cpu(%), ram(%)
    realtime_signal = pyqtSignal(float, float, float)


class ServerThread(threading.Thread):
    """
    Thread-ul în care rulează ServerCore ca să nu blocheze GUI-ul.
    Aici conectăm:
    - print() -> LogEmitter
    - ServerCore -> MetricsEmitter
    """
    def __init__(self, server_core, log_emitter, metrics_emitter):
        super().__init__(daemon=True)
        self.server_core = server_core
        self.log_emitter = log_emitter
        self.metrics_emitter = metrics_emitter

    def run(self):
        # 1. conectăm server_core la metrics_emitter
        self.server_core.set_metrics_emitter(self.metrics_emitter)

        # 2. monkey patch pentru print() ca să trimită log-uri în GUI
        original_print = print

        def custom_print(*args, **kwargs):
            message = ' '.join(map(str, args))
            self.log_emitter.log_signal.emit(message)
            original_print(*args, **kwargs)

        import builtins
        builtins.print = custom_print

        try:
            self.server_core.start()
        except Exception as e:
            self.log_emitter.log_signal.emit(f"[ERROR] {e}")
        finally:
            # restaurăm print-ul original
            builtins.print = original_print


class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server GUI - File Transfer Analyzer")
        self.setGeometry(200, 200, 900, 600)

        # --- instanțe logică server + emitters ---
        self.server_core = ServerCore()
        self.log_emitter = LogEmitter()
        self.metrics_emitter = MetricsEmitter()

        self.server_thread = None

        # conectăm semnalele
        self.log_emitter.log_signal.connect(self.update_log)
        self.metrics_emitter.realtime_signal.connect(self.update_realtime_charts)
        self.metrics_emitter.metrics_signal.connect(self.update_final_metrics)

        # --- UI ---
        self._setup_ui()

        # --- data pentru grafice ---
        self.throughput_data = []
        self.cpu_data = []
        self.ram_data = []
        self.sample_index = 0  # folosit ca X (0,1,2,...)

    # ==========================
    # UI setup
    # ==========================
    def _setup_ui(self):
        # butoane și status
        self.start_button = QPushButton("Start Server")
        self.stop_button = QPushButton("Stop Server")
        self.stop_button.setEnabled(False)

        self.status_label = QLabel("Status: Stopped")

        # tab widget
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

        # zona text pentru metrics finale
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setPlaceholderText("Transfer metrics will appear here after a file is received.")
        metrics_layout.addWidget(self.metrics_text)

        # grafice în grid: 2 x 2 (folosim doar 3)
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

        # adăugăm tab-urile în QTabWidget
        self.tabs.addTab(logs_tab, "Logs")
        self.tabs.addTab(metrics_tab, "Metrics & Charts")

        # layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.stop_button)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # conectăm butoanele
        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)

    # ==========================
    # Server control
    # ==========================
    def start_server(self):
        if self.server_thread is not None and self.server_thread.is_alive():
            return

        # resetăm graficele când pornim serverul (opțional)
        self.reset_charts()

        self.server_thread = ServerThread(
            self.server_core,
            self.log_emitter,
            self.metrics_emitter
        )
        self.server_thread.start()

        self.status_label.setText("Status: Running")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.update_log("[INFO] Server started.")

    def stop_server(self):
        self.server_core.stop()
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
        """
        Chemată din MetricsEmitter.realtime_signal
        de fiecare dată când ServerCore face sampling.
        """
        self.throughput_data.append(throughput)
        self.cpu_data.append(cpu)
        self.ram_data.append(ram)
        self.sample_index += 1

        x = list(range(len(self.throughput_data)))

        # actualizăm curbele
        self.throughput_curve.setData(x, self.throughput_data)
        self.cpu_curve.setData(x, self.cpu_data)
        self.ram_curve.setData(x, self.ram_data)

    def update_final_metrics(self, metrics: dict):
        """
        Chemată o singură dată la finalul transferului.
        metrics este rezultatul lui FileTransferMetrics.to_dict()
        """
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerWindow()
    window.show()
    sys.exit(app.exec_())
