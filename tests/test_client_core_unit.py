import os
import socket
import pytest

from client.client_core import ClientCore


class FakeSocket:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.connected_to = None
        self.sent_data = []
        self.closed = False

    def connect(self, addr):
        self.connected_to = addr
        if self.should_fail:
            raise ConnectionRefusedError("Simulated connect failure")

    def sendall(self, data: bytes):
        self.sent_data.append(data)

    def close(self):
        self.closed = True


def test_send_file_sends_header_and_body(monkeypatch, tmp_path):
    fake_socket = FakeSocket()

    def fake_socket_factory(*args, **kwargs):
        return fake_socket

    monkeypatch.setattr("client.client_core.socket.socket", fake_socket_factory, raising=True)

    content = b"hello-world-bytes"
    tmp_file = tmp_path / "sample.bin"
    tmp_file.write_bytes(content)

    client = ClientCore(host="127.0.0.1", port=5000)

    client.send_file(str(tmp_file))

    assert fake_socket.connected_to == ("127.0.0.1", 5000)

    all_sent = b"".join(fake_socket.sent_data)
    header_end = all_sent.find(b"\n")
    assert header_end != -1

    header = all_sent[: header_end + 1].decode()
    body = all_sent[header_end + 1 :]

    expected_name = os.path.basename(tmp_file)
    expected_size = os.path.getsize(tmp_file)
    expected_type = os.path.splitext(tmp_file)[1].lower()

    assert header == f"{expected_name}|{expected_size}|{expected_type}\n"
    assert body == content
    assert fake_socket.closed is True


def test_connect_raises_on_failure(monkeypatch):
    def failing_socket_factory(*args, **kwargs):
        return FakeSocket(should_fail=True)

    monkeypatch.setattr("client.client_core.socket.socket", failing_socket_factory, raising=True)

    client = ClientCore(host="127.0.0.1", port=5000)

    with pytest.raises(ConnectionRefusedError):
        client.connect()
