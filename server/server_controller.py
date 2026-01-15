from PyQt5.QtCore import QObject, pyqtSignal
from .server_core import ServerCore
import threading


class ServerController(QObject):
    # Qt signals for the view
    realtime_signal = pyqtSignal(float, float, float)  # throughput, cpu, ram
    metrics_signal = pyqtSignal(dict)  # final metrics dict

    def __init__(self, host=None, port=5000, save_dir="received_files"):
        super().__init__()
        self.server_core = ServerCore(host, port, save_dir)
        self.server_thread = None
        self._setup_callbacks()

    def _setup_callbacks(self):
        # Connect ServerCore callbacks to Qt signals
        self.server_core.on_realtime_metrics = self._emit_realtime_metrics
        self.server_core.on_final_metrics = self._emit_final_metrics

    def _emit_realtime_metrics(self, throughput, cpu, ram):
        self.realtime_signal.emit(throughput, cpu, ram)

    def _emit_final_metrics(self, metrics_dict):
        self.metrics_signal.emit(metrics_dict)


    def start_server(self):
        if self.server_thread is None or not self.server_thread.is_alive():
            self.server_thread = threading.Thread(target=self.server_core.start, daemon=True)
            self.server_thread.start()

    def stop_server(self):
        self.server_core.stop()
        if self.server_thread is not None:
            self.server_thread.join(timeout=1)
            self.server_thread = None
