import socket
import threading


def handle_client(conn, address):
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


def server_program():
    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server is listening on {host}:{port}")

    while True:
        conn, address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, address))
        thread.start()
        print(f"Active connections {threading.active_count() - 1}")


if __name__ == "__main__":
    server_program()