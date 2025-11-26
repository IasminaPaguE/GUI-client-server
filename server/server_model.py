import os
from typing import Optional, List

class FileTransferMetrics:
    def __init__(
        self,
        file_name: str,
        file_size: int,
        file_type: str,
        total_transfer_time: float,
        throughput: float,
        peak_throughput: float,
        transfer_byte_difference: int,
        transfer_status: str,
        cpu_usage_samples: Optional[List[float]] = None,
        ram_usage_samples: Optional[List[float]] = None
    ):
        self.file_name = file_name
        self.file_size = file_size
        self.file_type = file_type
        self.total_transfer_time = total_transfer_time
        self.throughput = throughput
        self.peak_throughput = peak_throughput
        self.transfer_byte_difference = transfer_byte_difference
        self.transfer_status = transfer_status
        self.cpu_usage_samples = cpu_usage_samples or []
        self.ram_usage_samples = ram_usage_samples or []

    @property
    def cpu_usage_avg(self):
        return sum(self.cpu_usage_samples) / len(self.cpu_usage_samples) if self.cpu_usage_samples else 0.0

    @property
    def cpu_usage_peak(self):
        return max(self.cpu_usage_samples) if self.cpu_usage_samples else 0.0

    @property
    def ram_usage_avg(self):
        return sum(self.ram_usage_samples) / len(self.ram_usage_samples) if self.ram_usage_samples else 0.0

    @property
    def ram_usage_peak(self):
        return max(self.ram_usage_samples) if self.ram_usage_samples else 0.0

    def to_dict(self):
        return {
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "total_transfer_time": self.total_transfer_time,
            "throughput": self.throughput,
            "peak_throughput": self.peak_throughput,
            "transfer_byte_difference": self.transfer_byte_difference,
            "transfer_status": self.transfer_status,
            "cpu_usage_avg": self.cpu_usage_avg,
            "cpu_usage_peak": self.cpu_usage_peak,
            "ram_usage_avg": self.ram_usage_avg,
            "ram_usage_peak": self.ram_usage_peak,
        }
