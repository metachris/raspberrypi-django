"""
Manages communication with GPIO and receiving commands

RPi.GPIO works with pin-ids instead of GPIO-ids (for instance GPIO17 has pin-id 11).

GPIO-Manager can also asynchronously run commands and replace existing timeouts on them with new ones.
"""
import yaml
import time
from threading import Thread

# Import either the dummy or the real lib
try:
    import RPi.GPIO as RPiGPIO
except:
    import dummy
    RPiGPIO = dummy.Dummy()


CONFIG_FILE = "config.yaml"

GPIO_TO_PIN_MAP = {
    # gpio-id: pin-id,
    17: 11,
}


class AsyncCmd(Thread):
    is_cancelled = False
    def __init__(self, timeout_sec, cmd, handle_cmd_cb, is_replaceable=True):
        # If is_replaceable is True and another timeout with the same command is added, the
        # existing timeout will be suspended and only the new one executed.
        Thread.__init__(self)
        self.timeout_sec = timeout_sec
        self.cmd = cmd
        self.handle_cmd_cb = handle_cmd_cb  # callback to execute command with
        self.is_replaceable = is_replaceable

    def run(self):
        time.sleep(self.timeout_sec)
        if not self.is_cancelled:
            self.handle_cmd_cb(self.cmd)


class GPIO(object):
    INPUT = RPiGPIO.IN
    OUTPUT = RPiGPIO.OUT
    HIGH = RPiGPIO.HIGH
    LOW = RPiGPIO.LOW

    config = None
    commands = None
    async_pool = []

    def __init__(self):
        RPiGPIO.setmode(RPiGPIO.BOARD)
        self._gpio_init()

    # Public Functions
    def gpio_setup(self, gpio_id, mode=OUTPUT):
        RPiGPIO.setup(self._gpioid_to_pinid(gpio_id), mode)

    def gpio_output(self, gpio_id, value=HIGH):
        RPiGPIO.output(self._gpioid_to_pinid(gpio_id), value)

    def cleanup(self):
        # Reset all channels that have been set up
        RPiGPIO.cleanup()

    def reload(self):
        self._gpio_init()

    def handle_cmd(self, cmd):
        # Called from tcp daemon if command comes in
        cmd = cmd.strip()
        print "cmd: '%s'" % cmd
        if cmd == "reload":
            self.reload()
        elif cmd in self.commands:
            # translate user-command to system-command and execute
            self._handle_cmd(self.commands[cmd])
        else:
            self._handle_cmd(cmd)

    # Internal Functions
    def _gpioid_to_pinid(self, gpio_id):
        # Translate gpio-id to pin-id
        return GPIO_TO_PIN_MAP[gpio_id]

    def _reload_config(self):
        self.config = yaml.load(open(CONFIG_FILE))
        print self.config
        self.commands = self.config["commands"]

    def _gpio_init(self):
        # Read config and set modes accordingly
        RPiGPIO.cleanup()

        self._reload_config()

        # Setup pins according to config file
        for gpio_id, mode in self.config.get("gpio-setup").items():
            if mode == "OUTPUT":
                mode = self.OUTPUT
            elif mode == "INPUT":
                mode = self.INPUT
            else:
                print "Error: cannot set mode to '%s' (_gpio_init)" % mode
                return

            # Setup pin to default mode from config file
            self.gpio_setup(gpio_id, mode)

    def _handle_cmd(self, internal_cmd):
        # Internal cmd is the actuall command (triggered by the user command)
        print "execute> %s" % internal_cmd
        cmd_parts = internal_cmd.split(" ")
        cmd = cmd_parts[0]
        if cmd == "set":
            gpio_id, value = cmd_parts[1:3]
            if value == "HIGH":
                value = self.HIGH
            elif value == "LOW":
                value = self.LOW
            else:
                print "Error cannot handle command '%s' due to bad value" % internal_cmd
                return
            self.gpio_output(int(gpio_id), value)

        elif cmd == "rtimeout":
            # Replaceable timeout. Replaces based on "cmd" only.
            timeout = cmd_parts[1]
            cmd = " ".join(cmd_parts[2:])
            print "understood rtimeout. cmd in %s seconds: `%s`" % (timeout, cmd)

            # Disable all old ones from the pool
            for async_cmd in self.async_pool:
                if async_cmd.cmd == cmd and async_cmd.is_replaceable:
                    async_cmd.is_cancelled = True

            # Remove cancelled threads from the pool
            self.async_pool[:] = [t for t in self.async_pool if not t.is_cancelled]

            # Now add new task
            t = AsyncCmd(int(timeout), cmd, self.handle_cmd, is_replaceable=True)
            t.start()
            self.async_pool.append(t)

        else:
            print "command not recognized"


if __name__ == "__main__":
    # Some testing
    g = GPIO()
    g.handle_cmd("thermo on")
    g.handle_cmd("rtimeout 3 thermo off")
    time.sleep(1)
    g.handle_cmd("rtimeout 3 thermo off")
    time.sleep(1)
    g.handle_cmd("rtimeout 3 thermo off")
    time.sleep(1)

    g.handle_cmd("rtimeout 3 thermo off")

    time.sleep(5)
    g.cleanup()
