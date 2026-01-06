import socket
import threading

# --- Server Configuration & Global State ---
HOST = "0.0.0.0"  
PORT = 42069      

clients = {}

def start_server():
    """
    Initializes the TCP server, binds it to the host/port, and begins listening.
    """
    print(f"[*] Server is starting on {HOST}:{PORT}...")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server_socket.bind((HOST, PORT))
        
        # Enable the server to accept connections (backlog of 5)
        server_socket.listen(5)
        print("[*] Server is listening for incoming connections...")

        while True:
            # Accept a new connection
            client_socket, client_address = server_socket.accept()
            print(f"[+] New connection from {client_address}")

            # Create and start a dedicated thread for this client
            thread = threading.Thread(target=handle_client, args=(client_socket, ))
            thread.start()
            
    except Exception as e:
        print(f"[!] Critical Server Error: {e}")
    finally:
        server_socket.close()

def broadcast_connected_users():
    """
    Sends the updated list of currently connected users to all clients.
    """
    users = ",".join(clients.keys())
    message = f"USERS_LIST:{users}"
    
    for name, sock in clients.items():
        try:
            sock.send(message.encode('utf-8'))
        except Exception as e:
            print(f"[!] Error broadcasting user list to {name}: {e}")

    return message

def broadcast_message(message):
    """
    Sends a general message to all connected clients.
    """
    for name, client_socket in clients.items():
        try:
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            # this catch block prevents the server from crashing on broadcast.
            pass

def handle_client(client_socket):
    """
    Manages the lifecycle of a single client connection.
    
    """
    client_name = None
    try:
        # Handshake / Login 
        login_message = "LOGIN_REQUEST"
        client_socket.send(login_message.encode('utf-8'))
        
        # Wait for the client to send their username
        client_name = client_socket.recv(1024).decode('utf-8')
        print(f"[+] User logged in: {client_name}")

        # Register the client
        clients[client_name] = client_socket
        
        # Notify everyone about the new user
        broadcast_connected_users()
        connection_message = f"'{client_name}' connected.."
        broadcast_message(connection_message)

        # Main Message Loop
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                # Empty data implies the client closed the connection
                break
            
            decoded_message = data.decode('utf-8')
            
            # Protocol Parsing
            # Expected format for private messages: "TargetUsername:MessageContent"
            if ':' in decoded_message:
                partner_name, message = decoded_message.split(":", 1)

                if partner_name in clients:
                    try:
                        partner_socket = clients[partner_name]
                        # Forward the message: "SenderName: MessageContent"
                        partner_socket.send((f"{client_name}: {message}").encode('utf-8'))                
                        
                        print(f"[{client_name}] sent message to [{partner_name}]: {decoded_message}")
         
                    except Exception as e:
                        # Handle case where socket exists but sending fails
                        client_socket.send(f"System: User '{partner_name}' seems to be disconnected.".encode('utf-8'))
                else:
                    # User not found in the dictionary
                    error_msg = f"System: User '{partner_name}' is currently offline."
                    client_socket.send(error_msg.encode('utf-8'))
                
    except (ConnectionResetError, ConnectionAbortedError):
        # Client forcibly closed the connection
        pass

    except Exception as e:
        print(f"[!] Error handling client '{client_name}': {e}")
    
    finally:
        if client_name:
            print(f"[-] Client '{client_name}' disconnected.")
            
            
            disconnected_message = f"'{client_name}' disconnected.."
            broadcast_message(disconnected_message)

            clients.pop(client_name, None)
            broadcast_connected_users()

        client_socket.close()

if __name__ == "__main__":
    start_server()