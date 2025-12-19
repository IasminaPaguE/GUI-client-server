import os
import time

import pytest

from server.server_core import ServerCore
from server.server_model import FileTransferMetrics


class FakeConn:
    def __init__(self, payload: bytes):
        self._payload = bytearray(payload)
        self.closed = False

    def recv(self, n: int) -> bytes:
        if not self._payload:
            return b""
        chunk = self._payload[:n]
        del self._payload[:n]
        return bytes(chunk)

    def close(self) -> None:
        self.closed = True


def _run_handle_client_with_header_and_body(tmp_path, header: str, body: bytes):
    server = ServerCore(host="127.0.0.1", port=0, save_dir=str(tmp_path))

    metrics_list = []

    def on_final(metrics_dict):
        metrics_list.append(metrics_dict)

    server.on_final_metrics = on_final

    payload = header.encode() + body
    conn = FakeConn(payload)

    server.handle_client(conn, ("127.0.0.1", 12345))

    assert conn.closed is True
    assert metrics_list, "No metrics were reported by on_final_metrics callback"
    return metrics_list[0]


def test_handle_client_parses_valid_header_and_saves_file(tmp_path):
    body = b"hello world" * 10
    expected_size = len(body)
    header = f"testfile.bin|{expected_size}|.bin\n"

    metrics = _run_handle_client_with_header_and_body(tmp_path, header, body)

    saved_path = os.path.join(tmp_path, "testfile.bin")
    assert os.path.exists(saved_path)
    with open(saved_path, "rb") as f:
        saved_data = f.read()

    assert saved_data == body

    assert metrics["file_name"] == "testfile.bin"
    assert metrics["file_size"] == expected_size
    assert metrics["file_type"] == ".bin"
    assert metrics["transfer_status"] == "Success"
    assert metrics["transfer_byte_difference"] == 0


def test_handle_client_handles_malformed_header(tmp_path):
    body = b"data-without-valid-header"
    header = "not-a-valid-header\n"

    metrics = _run_handle_client_with_header_and_body(tmp_path, header, body)

    saved_path = os.path.join(tmp_path, "unknown")
    assert os.path.exists(saved_path)

    assert metrics["file_name"] == "unknown"
    assert metrics["file_type"] == ""
    assert metrics["transfer_status"] == "Failed"


def test_handle_client_incomplete_transfer_marks_failed(tmp_path):
    full_size = 4096
    sent_size = 1024
    body = b"x" * sent_size
    header = f"partial.bin|{full_size}|.bin\n"

    metrics = _run_handle_client_with_header_and_body(tmp_path, header, body)

    assert metrics["file_name"] == "partial.bin"
    assert metrics["file_size"] == full_size
    assert metrics["transfer_status"] == "Failed"
    assert metrics["transfer_byte_difference"] == full_size - sent_size


def test_file_transfer_metrics_computes_cpu_and_ram_stats():
    metrics = FileTransferMetrics(
        file_name="file.bin",
        file_size=100,
        file_type=".bin",
        total_transfer_time=1.0,
        throughput=10.0,
        peak_throughput=15.0,
        transfer_byte_difference=0,
        transfer_status="Success",
        cpu_usage_samples=[10.0, 20.0, 30.0],
        ram_usage_samples=[40.0, 50.0],
    )

    assert metrics.cpu_usage_avg == pytest.approx(20.0)
    assert metrics.cpu_usage_peak == pytest.approx(30.0)
    assert metrics.ram_usage_avg == pytest.approx(45.0)
    assert metrics.ram_usage_peak == pytest.approx(50.0)

    as_dict = metrics.to_dict()
    expected_keys = {
        "file_name",
        "file_size",
        "file_type",
        "total_transfer_time",
        "throughput",
        "peak_throughput",
        "transfer_byte_difference",
        "transfer_status",
        "cpu_usage_avg",
        "cpu_usage_peak",
        "ram_usage_avg",
        "ram_usage_peak",
    }
    assert expected_keys.issubset(as_dict.keys())
