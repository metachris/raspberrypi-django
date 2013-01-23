import traceback

from tornado.ioloop import IOLoop
from tornado.netutil import TCPServer

import gpiomanager


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


class GPIOServer(TCPServer):
    def __init__(self, gpio, io_loop=None, ssl_options=None, **kwargs):
        self.GPIO = gpio
        TCPServer.__init__(self, io_loop=io_loop, ssl_options=ssl_options, **kwargs)
        print 'GPIOServer started'

    def handle_stream(self, stream, address):
        TCPConnection(self.GPIO, stream, address)


def main():
    GPIO = gpiomanager.GPIO()
    chat_server = GPIOServer(GPIO)
    chat_server.listen(9101)

    try:
        IOLoop.instance().start()
    except:
        print traceback.format_exc()
    finally:
        GPIO.cleanup()
        print "GPIOServer stopped"

if __name__ == '__main__':
    main()
