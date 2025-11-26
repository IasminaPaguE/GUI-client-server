
import socket
import os
import threading
import time
import psutil
from .server_model import FileTransferMetrics

class ServerCore:
    def __init__(self, host=None, port=5000, save_dir="received_files"):
        self.host = host or socket.gethostname()
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def start(self):
        self.server_socket = socket.socket()
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server is listening on {self.host}:{self.port}")
        self.is_running = True
        while self.is_running:
            conn, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
            client_thread.start()
            print(f"Active connections {threading.active_count() - 1}")

    def handle_client(self, conn, addr):
        try:
            # First, receive the metadata header: <file_name>|<file_size>|<file_type>\n
            header_bytes = b""
            while True:
                byte = conn.recv(1)
                if byte == b"\n" or not byte:
                    break
                header_bytes += byte
            header = header_bytes.decode(errors="ignore")
            try:
                file_name, file_size_str, file_type = header.split('|')
                expected_size = int(file_size_str)
            except Exception:
                file_name = "unknown"
                file_type = ""
                expected_size = None

            print(f"Receiving file: {file_name} from {addr}")
            file_path = os.path.join(self.save_dir, file_name)

            # Metrics collection
            start_time = time.time()
            bytes_received = 0
            throughput_samples = []
            cpu_samples = []
            ram_samples = []
            last_sample_time = start_time
            # Always take at least one sample
            cpu_samples.append(psutil.cpu_percent(interval=None))
            ram_samples.append(psutil.virtual_memory().percent)

            sample_interval = 0.00000000000000000000000000000000000000000000000000005  # 50ms
            with open(file_path, "wb") as f:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    f.write(data)
                    bytes_received += len(data)
                    # Sample throughput, CPU, RAM every 50ms
                    now = time.time()
                    if now - last_sample_time >= sample_interval:
                        elapsed = now - start_time
                        if elapsed > 0:
                            throughput_samples.append(bytes_received / elapsed / (1024*1024))  # MB/s
                        cpu_samples.append(psutil.cpu_percent(interval=None))
                        ram_samples.append(psutil.virtual_memory().percent)
                        last_sample_time = now
            stop_time = time.time()
            total_transfer_time = stop_time - start_time
            avg_throughput = (bytes_received / total_transfer_time) / (1024*1024) if total_transfer_time > 0 else 0.0
            peak_throughput = max(throughput_samples) if throughput_samples else avg_throughput
            transfer_byte_difference = (expected_size - bytes_received) if expected_size is not None else 0
            transfer_status = "Success" if expected_size == bytes_received else "Failed"

            metrics = FileTransferMetrics(
                file_name=file_name,
                file_size=expected_size if expected_size is not None else bytes_received,
                file_type=file_type,
                total_transfer_time=total_transfer_time,
                throughput=avg_throughput,
                peak_throughput=peak_throughput,
                transfer_byte_difference=transfer_byte_difference,
                transfer_status=transfer_status,
                cpu_usage_samples=cpu_samples,
                ram_usage_samples=ram_samples
            )
            print(f"File saved: {file_path}")
            print("Transfer metrics:", metrics.to_dict())
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            conn.close()

    def stop(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        print("Server Oprit.")
