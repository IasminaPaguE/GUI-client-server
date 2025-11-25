import socket

class ClientCore:
    def __init__(self, host = None, port = 5000):
        self.host = host or socket.gethostname() 
        self.port = 5000
        self.client_socket = None
        self.is_running = False

    def connect(self):
        self.client_socket = socket.socket()
        self.client_socket.connect((self.host, self.port))
        print("I m connecting to the server")

    def chat(self):
        self.connect()
        message = input(" -> ")
        is_running = True
        
        while is_running:
            self.client_socket.send(message.encode())
            data = self.client_socket.recv(1024).decode()

            print("Received from server " + data)

            message = input(" -> ")
            if message.lower().strip() == 'bye':
                is_running = False

        self.client_socket.close()

    def send_file(self, file_path):
        import os
        self.connect()
        filename = os.path.basename(file_path)
        # Send filename followed by newline
        self.client_socket.send((filename + '\n').encode())
        with open(file_path, 'rb') as f:
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    break
                self.client_socket.sendall(bytes_read)
        self.client_socket.close()
