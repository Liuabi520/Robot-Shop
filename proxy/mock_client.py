import socket


def send_via_proxy(proxy_host, proxy_port, target_address, request):
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to the proxy server
        sock.connect((proxy_host, proxy_port))

        # Send the target address followed by a newline character
        sock.sendall(f"{target_address}\n".encode("utf-8"))

        # Send the actual HTTP request
        sock.sendall(request.encode("utf-8"))

        # Receive the response from the proxy server
        response = b""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data
            print(response.decode("utf-8"))
    # Print the response data


# Example usage
proxy_host = "localhost"
proxy_port = 8899
target_address = "httpforever.com:80"
http_request = "GET / HTTP/1.1\r\nHost: httpforever.com\r\n\r\n"

send_via_proxy(proxy_host, proxy_port, target_address, http_request)
