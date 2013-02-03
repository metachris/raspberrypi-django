import socket

HOST, PORT = "localhost", 9101

class GPIOClient(object):
    def __init__(self):
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((HOST, PORT))
        return self

    def send(self, data):
        self.sock.sendall(data + "\n")

    def close(self):
        self.sock.sendall("\n")
        self.sock.close()
