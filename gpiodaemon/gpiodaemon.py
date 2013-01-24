#!/usr/bin/env python
import sys
import signal
import socket
import traceback
from os import getpid, remove, kill
from optparse import OptionParser
from time import sleep

from tornado.ioloop import IOLoop
from tornado.netutil import TCPServer

import gpiomanager

PORT = 9101
PIDFILE = "/tmp/gpiodaemon.pid"

# We shut the daemon down by sending the SIGINT signal to this process
# (eg $ kill -s SIGINT [proc-id])
def signal_handler(signal, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


# Each connected client gets a TCPConnection object
class TCPConnection(object):
    def __init__(self, gpio, stream, address):
        print '- new connection from %s' % repr(address)
        self.GPIO = gpio
        self.stream = stream
        self.address = address
        self.stream.set_close_callback(self._on_close)
        self.stream.read_until('\n', self._on_read_line)

    def _on_read_line(self, data):
        data = data.strip()
        if not data or data == "quit":
            self.stream.close()
            return


        print '- from %s: "%s"' % (repr(self.address), data)
        self.GPIO.handle_cmd(data)
        self.stream.read_until('\n', self._on_read_line)

    def _on_write_complete(self):
        pass

    def _on_close(self):
        print '- client quit %s' % repr(self.address)


# The one main server
class GPIOServer(TCPServer):
    def __init__(self, gpio, io_loop=None, ssl_options=None, **kwargs):
        self.GPIO = gpio
        TCPServer.__init__(self, io_loop=io_loop, ssl_options=ssl_options, **kwargs)
        print 'GPIOServer started'

    def handle_stream(self, stream, address):
        TCPConnection(self.GPIO, stream, address)


# Setup & Startup
def main():
    with open(PIDFILE, "w") as f:
        f.write("%s" % getpid())

    GPIO = gpiomanager.GPIO()
    chat_server = GPIOServer(GPIO)
    chat_server.listen(PORT)

    try:
        IOLoop.instance().start()
    except SystemExit:
        print "Shutting down via signal"
    except:
        print traceback.format_exc()
    finally:
        GPIO.cleanup()
        print "GPIOServer stopped"

    remove(PIDFILE)


def daemon_shutdown():
    """Shuts down a daemon running on localhost by sending SIGINT"""
    pid = open(PIDFILE).read()
    kill(int(pid), signal.SIGINT)


def daemon_reload():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("localhost", PORT))
        sock.sendall("reload\n\n")  # second newline (empty packet) terminates the connection server-side
    finally:
        sock.close()


if __name__ == '__main__':
    usage = """usage: %prog [OPTION]"""
    desc="""GPIO-Daemon is little program to help dealing with/programming the GPIO ports on the
    Raspberry pi via a socket interface (eg. telnet). The daemon listens on port %s for TCP
    connections and can execute commands as well as schedule them.""" % PORT
    parser = OptionParser(usage=usage, description=desc)

    parser.add_option("--start", default=False,
        action="store_true", dest="start", help="start gpio daemon")

    parser.add_option("--stop", default=False,
        action="store_true", dest="stop", help="stop a gpio daemon")

    parser.add_option("--reload", default=False,
        action="store_true", dest="reload", help="reload the configuration and reset gpio pins")

    parser.add_option("--restart", default=False,
        action="store_true", dest="restart", help="stop the daemon and start a new one")

    (options, args) = parser.parse_args()
    if options.start:
        main()

    elif options.stop:
        daemon_shutdown()

    elif options.reload:
        daemon_reload()

    elif options.restart:
        print "Shutting down daemon..."
        daemon_shutdown()
        sleep(5)
        main()

    else:
        parser.print_help()
