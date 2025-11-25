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
