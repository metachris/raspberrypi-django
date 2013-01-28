import time
import socket
import errno
import signal

from traceback import format_exc
from threading import Thread

import logging
from logging import debug, error

from tornado import ioloop


HOST, PORT = "localhost", 9101



class TCPClient(object):
    """A non-blocking TCP client implemented with ioloop

    IO is an instance of ioloop (by default, tornado ioloop instance will be used).
    TCP client usage code example:

        client = TCPClient(host, port)
        client.start()
    """
    read_chunk_size = 1024

    def __init__(self, io=None):
        """Initialize TCP client object via passing connection handler's class

        If empty ioloop param is passed, server will use instance of IOLoop
        singleton from ``tornado`` package.
        """
        self.io_loop = io or ioloop.IOLoop.instance()

    def connect(self, host, port):
        """Create object of nonblocking socket and connect to given addr"""
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.host, self.port))
        self.sock.setblocking(0)

        self.io_loop.add_handler(
            self.sock.fileno(), self._handle_events, self.io_loop.ERROR)
        self.io_loop.update_handler(self.sock.fileno(), self.io_loop.READ)

        return self

    def _handle_events(self, fd, events):
        if not self.sock:
            print "Got events for closed stream %d" % fd
            return
        if events & self.io_loop.READ:
            self._handle_read()
        if events & self.io_loop.ERROR:
            self._close_socket()
            return

    def _close_socket(self):
        try:
            self.io_loop.remove_handler(self.sock.fileno())
        except:
            pass

        if self.sock:
            self.sock.close()
            self.sock = None

    def _handle_read(self):
        """Signal by epoll: data chunk ready to read from socket buffer."""
        try:
            chunk = self.sock.recv(self.read_chunk_size)
        except socket.error, e:
            if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                return
            else:
                print "Read error on %d: %s" % (self.fileno, e)
                self._close_socket()
                return

        # empty data means closed socket per TCP specs
        if not chunk:
            self._close_socket()
            return

        self.handle_read(chunk.strip())

    def handle_read(self, data):
        """Overwrite with custom implementation"""
        pass


class GPIOClientThread(TCPClient, Thread):
    def __init__(self):
        Thread.__init__(self)
        TCPClient.__init__(self)

        #signal.signal(signal.SIGINT, self.signal_handler)

    # Catch SIGINT to shut the daemon down (eg. via $ kill -s SIGINT [proc-id])
    def signal_handler(self, signal, frame):
        print "shutting down via signal"
        self.close()


    def send(self, data):
        print "sending '%s' to GPIO daemon..." % data
        self.sock.send("%s\n" % data)

    def close(self):
        try:
            self.sock.send("\n")
        finally:
            self._close_socket()
            self.io_loop.stop()

    def run(self):
        "Starting ioloop instance in thread"
        self.connect(HOST, PORT)
        self.io_loop.start()

    def handle_read(self, data):
        print "Chunk received: '%s'" % data


if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(format='%(levelname)s | %(asctime)s | %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    client = GPIOClientThread()
    client.start()

    time.sleep(3)
    client.sock.send("read 12\n")

    print "waiting..."
    time.sleep(100)
    print 'end'
