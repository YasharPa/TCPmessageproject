import socket
import threading

HOST = "0.0.0.0"
PORT = 42069

def start_server():
    print("server is up...(ah ki dolev amar)")
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((HOST,PORT))

    #min people
    server_socket.listen(5)

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connected to: {client_socket} {client_address}")
        thread = threading.Thread(target=handle_client, args=(client_socket, ))
        thread.start()
        
def handle_client(client_socket):

    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        decoded_message = data.decode('utf-8')
        print(f"message: {decoded_message}")

    client_socket.close()

if __name__ == "__main__":
    start_server()