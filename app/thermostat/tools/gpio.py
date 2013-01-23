import socket

HOST, PORT = "localhost", 9101

def send_to_gpio_daemon(data):
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(data + "\n")

    finally:
        sock.close()
