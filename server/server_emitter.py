from PyQt5.QtCore import QObject, pyqtSignal

class LogEmitter(QObject):
    log_signal = pyqtSignal(str)

class MetricsEmitter(QObject):
    # dict cu metrics finale (to_dict() din FileTransferMetrics)
    metrics_signal = pyqtSignal(dict)
    # throughput(MB/s), cpu(%), ram(%)
    realtime_signal = pyqtSignal(float, float, float)
