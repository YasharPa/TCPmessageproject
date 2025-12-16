import socket
import threading

ADDRESS = "127.0.0.1"
PORT = 42069
clients = {}


def start_client():
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((ADDRESS, PORT))
    
    thread = threading.Thread(target=get_messages, args=(client_socket,))
    thread.start()


    while True:
        message = input(":>> ")
        client_socket.send(message.encode('utf-8'))

def get_messages(server_socket):
    try:
        while True:
            data = server_socket.recv(1024)
            if not data:
                break
            decoded_message =  data.decode('utf-8')
            print(f"message from {data.fd}: {decoded_message}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
             




if __name__ == "__main__":
    start_client()
    