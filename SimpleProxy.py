import socket
import threading

def handle_client(client_socket):
    # Receive the target address from the client
    target_address = client_socket.recv(4096).decode('utf-8')
    print(f"[*] Received target address: {target_address}")
    target_host, target_port = target_address.split('\n')[0].split(':')
    target_port = int(target_port)
    
    # Connect to the target server
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect((target_host, target_port))
    
    # Relay data
    while True:
        # From client to target
        data = "\n".join(target_address.split('\n')[1:]).encode('utf-8')
        print("Data: ", data)
        if not data:
            break
        target_socket.send(data)
        
        # From target to client
        response = target_socket.recv(4096)
        if not response:
            break
        client_socket.send(response)
    
    client_socket.close()
    target_socket.close()

def start_proxy(local_host, local_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_host, local_port))
    server.listen(5)
    print(f"[*] Listening on {local_host}:{local_port}")

    while True:
        client_socket, _ = server.accept()
        print(f"[*] Accepted connection from {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    LOCAL_HOST = '127.0.0.1'
    LOCAL_PORT = 9998
    start_proxy(LOCAL_HOST, LOCAL_PORT)