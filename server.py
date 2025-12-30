import socket
import threading

HOST = "0.0.0.0"
PORT = 42069
clients = {}

def start_server():
    print("server is up...")
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((HOST,PORT))

    #min people
    server_socket.listen(5)

    while True:
        client_socket, client_address = server_socket.accept()                
        
        thread = threading.Thread(target=handle_client, args=(client_socket, ))
        thread.start()
        

def broadcast_connected_users():
    users = ",".join(clients.keys())
    message = f"USERS_LIST:{users}"
    
    for name, sock in clients.items():
        try:
            sock.send(message.encode('utf-8'))
        except:
            pass

    return message

def broadcast_message(message):

    for name, client_socket in clients.items():
        try:
            client_socket.send(message.encode('utf-8'))
        except:
            pass

def handle_client(client_socket):
    client_name = None
    try:

        login_message = "LOGIN_REQUEST"
        encoded_login_message = login_message.encode('utf-8')
        client_socket.send(encoded_login_message)
        client_name = client_socket.recv(1024).decode('utf-8')
        print(client_name)

        
        clients[client_name] = client_socket
        broadcast_connected_users()
        connection_message = f"'{client_name}' connected.."
        broadcast_message(connection_message)
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                break
            
            decoded_message = data.decode('utf-8')
            if(':' in decoded_message):
                partner_name, message = decoded_message.split(":", 1)

                if partner_name in clients:
                    try:
                        partner_socket = clients[partner_name]
                        partner_socket.send((f"{client_name}: {message}").encode('utf-8'))                
                        # server log
                        print(f"[{client_name}] sent message to [{partner_name}]: {decoded_message}")
         
                    except:
                        client_socket.send(f"System: User '{partner_name}' seems to be disconnected.".encode('utf-8'))
                else:
                    error_msg = f"System: User '{partner_name}' is currently offline."
                    client_socket.send(error_msg.encode('utf-8'))
                
    except (ConnectionResetError, ConnectionAbortedError):
        pass

    except Exception as e:
        print(f"Error with client {client_name}: {e}")
    
    finally:    
        disconnected_message = f"'{client_name}' disconnected.."
        print(disconnected_message) 
        broadcast_message(disconnected_message)

        clients.pop(client_name, None)
        broadcast_connected_users()

    client_socket.close()


if __name__ == "__main__":
    start_server()

