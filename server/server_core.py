import socket
import threading

class ServerCore:
    def __init__(self, host=None, port=5000):
        self.host = host or socket.gethostname()
        self.port = port
        self.server_socket = None
        self.is_running = False

    def handle_client(self, conn, address):
        print("Connection from " + str(address))
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    print(f"Connection ended {address}")
                    break
                print(f"From {address}: {data}")
                response = input(" -> ")
                conn.send(response.encode())
            except ConnectionResetError:
                print(f"Error Connection reset by {address}")
                break
        conn.close()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.is_running = True

        print(f"Server is listening on {self.host}:{self.port}")

        while self.is_running:
            conn, address = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, address))
            thread.start()
            print(f"Active connections {threading.active_count() - 1}")

    def stop(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        print("Server Oprit.")
