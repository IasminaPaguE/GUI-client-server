
import socket
import os
import threading

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
            # First, receive the filename (assume <filename>\n)
            filename_bytes = b""
            while True:
                byte = conn.recv(1)
                if byte == b"\n" or not byte:
                    break
                filename_bytes += byte
            filename = filename_bytes.decode(errors="ignore")
            print(f"Receiving file: {filename} from {addr}")
            file_path = os.path.join(self.save_dir, filename)
            with open(file_path, "wb") as f:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    f.write(data)
            print(f"File saved: {file_path}")
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            conn.close()

    def stop(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        print("Server Oprit.")
