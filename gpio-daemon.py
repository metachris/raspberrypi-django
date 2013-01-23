# Simple Daemon to control the GPIOs
#
# Listens on TCP port 9101
#
# Commands:
#   thermo on
#   thermo off
#

import SocketServer
import threading
import time

# Import either the dummy or the real lib
try:
    import GPIODummy
    GPIO = GPIODummy.DummyGPIO()
except:
    import RPi.GPIO as GPIO


# Pool to collect the threads
threadpool = []

# General GPIO Setup
def setup_GPIO():
    GPIO.setmode(GPIO.BOARD)

    # 11 is GPIO-17 (Thermo Controller)
    GPIO.setup(11, GPIO.OUT)

    print "GPIO Setup Complete"


# Thread to turn off heat (or run any def) after a timeout
class RunAfterIntervalThread(threading.Thread):
    is_cancelled = False
    def __init__(self, timeout_sec, to_run):
        threading.Thread.__init__(self)
        self.timeout_sec = timeout_sec
        self.to_run = to_run

    def run(self):
        time.sleep(self.timeout_sec)
        if not self.is_cancelled and self.to_run:
            self.to_run()


def thermo_turn_off():
    GPIO.output(11, GPIO.LOW)
    print "- Thermo turned off"


def thermo_turn_on():
    GPIO.output(11, GPIO.HIGH)

    # Cancel all previous deactivation-threads and start a new one
    global threadpool
    for t in threadpool:
        t.is_cancelled = True
    t = RunAfterIntervalThread(5, thermo_turn_off)
    t.start()
    threadpool.append(t)
    print "- Thermo turned on"


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "%s wrote: %s" % (self.client_address[0], self.data)

        if self.data == "thermo on":
            thermo_turn_on()
        elif self.data == "thermo off":
            thermo_turn_off()

        # just send back the same data, but upper-cased
        #self.request.sendall(self.data.upper())


if __name__ == "__main__":
    HOST, PORT = "localhost", 9101

    setup_GPIO()

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
