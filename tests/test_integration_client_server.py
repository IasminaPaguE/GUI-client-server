import os
import socket
import threading
import time

import pytest

from client.client_core import ClientCore
from server.server_core import ServerCore


@pytest.fixture
def running_server(tmp_path):
    server = ServerCore(host="127.0.0.1", port=0, save_dir=str(tmp_path))

    final_metrics = []
    server_errors = []

    def on_final(metrics_dict):
        final_metrics.append(metrics_dict)

    server.on_final_metrics = on_final

    def run_server():
        try:
            server.start()
        except Exception as exc:  # pragma: no cover - captured for assertions
            server_errors.append(exc)

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    timeout = time.time() + 5
    while server.server_socket is None and time.time() < timeout:
        time.sleep(0.01)

    assert server.server_socket is not None, "Server socket failed to start"
    host, port = server.server_socket.getsockname()

    yield {
        "server": server,
        "thread": thread,
        "host": host,
        "port": port,
        "metrics": final_metrics,
        "errors": server_errors,
        "save_dir": str(tmp_path),
    }

    server.stop()
    thread.join(timeout=5)
    assert not server_errors, f"Server thread raised errors: {server_errors}"


def _wait_for_metrics(metrics_list, expected_count=1, timeout_seconds=5):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if len(metrics_list) >= expected_count:
            return
        time.sleep(0.05)
    raise AssertionError("Timed out waiting for metrics")


def test_server_startup_accepts_connection(running_server):
    host = running_server["host"]
    port = running_server["port"]

    s = socket.socket()
    s.connect((host, port))
    s.close()

    time.sleep(0.2)


def test_small_file_transfer(running_server, tmp_path):
    host = running_server["host"]
    port = running_server["port"]
    metrics_list = running_server["metrics"]
    save_dir = running_server["save_dir"]

    content = b"a" * 1024
    src_file = tmp_path / "small.bin"
    src_file.write_bytes(content)

    client = ClientCore(host=host, port=port)
    client.send_file(str(src_file))

    _wait_for_metrics(metrics_list, expected_count=1)

    # Find metrics for this specific file
    m = next(mm for mm in metrics_list if mm["file_name"] == "small.bin")
    saved_path = os.path.join(save_dir, m["file_name"])

    # Server should create an output file and record metrics for it.
    assert os.path.exists(saved_path)
    assert m["file_name"] == "small.bin"
    assert m["file_size"] == len(content)


def test_large_file_transfer_10mb(running_server, tmp_path):
    host = running_server["host"]
    port = running_server["port"]
    metrics_list = running_server["metrics"]
    save_dir = running_server["save_dir"]

    size_bytes = 10 * 1024 * 1024
    content = b"b" * size_bytes
    src_file = tmp_path / "large.bin"
    src_file.write_bytes(content)

    client = ClientCore(host=host, port=port)
    client.send_file(str(src_file))

    # Only this transfer runs in this test, so wait for one metrics entry
    _wait_for_metrics(metrics_list, expected_count=1)

    m = next(mm for mm in metrics_list if mm["file_name"] == "large.bin")

    saved_path = os.path.join(save_dir, m["file_name"])
    assert os.path.exists(saved_path)

    # Validate that the server recorded correct header metadata for the file.
    assert m["file_name"] == "large.bin"
    assert m["file_size"] == size_bytes


def test_simultaneous_transfers(running_server, tmp_path):
    host = running_server["host"]
    port = running_server["port"]
    metrics_list = running_server["metrics"]

    def send_named_file(name: str, data: bytes):
        path = tmp_path / name
        path.write_bytes(data)
        client = ClientCore(host=host, port=port)
        client.send_file(str(path))

    contents = {
        "c1.bin": b"x" * 2048,
        "c2.bin": b"y" * 2048,
        "c3.bin": b"z" * 2048,
    }

    threads = []
    for name, data in contents.items():
        t = threading.Thread(target=send_named_file, args=(name, data))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # Each thread sends a single file in this test
    _wait_for_metrics(metrics_list, expected_count=len(contents))

    # Ensure the server handled all transfers and produced metrics entries.
    for name in contents.keys():
        matching = [m for m in metrics_list if m["file_name"] == name]
        assert matching, f"No metrics found for {name}"


def test_client_disconnect_mid_transfer_marked_failed(running_server):
    host = running_server["host"]
    port = running_server["port"]
    metrics_list = running_server["metrics"]

    expected_size = 10240
    sent_size = 1024

    header = f"incomplete.bin|{expected_size}|.bin\n".encode()
    body = b"d" * sent_size

    s = socket.socket()
    s.connect((host, port))
    s.sendall(header + body)
    s.close()

    # Only one incomplete transfer is performed in this test
    _wait_for_metrics(metrics_list, expected_count=1)

    m = next(mm for mm in metrics_list if mm["file_name"] == "incomplete.bin")
    assert m["transfer_status"] == "Failed"
    assert m["transfer_byte_difference"] == expected_size - sent_size
