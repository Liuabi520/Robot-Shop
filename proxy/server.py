import socket
import threading
import datetime


def log(msg):
    with open(LOG_FILE, "a") as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {msg}\n")
        print(f"\033[34m[{timestamp}] {msg}\033[0m")


def handle_client(client_socket):
    # simple handshake: the first line should be the target address
    target_addr = b""
    while True:
        data = client_socket.recv(1)
        if data == b"\n":
            break
        target_addr += data
    target_addr = target_addr.decode("utf-8").strip()
    target_host, target_port = target_addr.split(":")
    target_port = int(target_port)
    log(f"Received target address: {target_host} {target_port}")

    # connect to the target server
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect((target_host, target_port))

    # the loop of proxying data
    while True:
        # read from client and send to target
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            log("Client disconnected")
            break
        log(f"Relaying request to target\n===\n{data}\n===")
        target_socket.send(data)

        # get the response from the target and send it back to the client
        response = target_socket.recv(BUFFER_SIZE)
        if not response:
            log("Target disconnected")
            break
        log(f"Relaying response to client\n===\n{response}\n===")
        client_socket.send(response)

    client_socket.close()
    target_socket.close()


def start_proxy(local_host, local_port):  
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_host, local_port))
    server.listen(5)
    log(f"Listening on {local_host}:{local_port}")
    while True:
        client_socket, _ = server.accept()
        log(
            f"Accepted connection from {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}"
        )
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


if __name__ == "__main__":
    LOCAL_PORT = 8899
    LOG_FILE = "log.txt"
    BUFFER_SIZE = 4096
    try:
        start_proxy("", LOCAL_PORT)
    except KeyboardInterrupt:
        log("Proxy server is shutting down")
        server.close()
