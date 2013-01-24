"""
Receives user-commands and communicates with the RPi.GPIO lib to switch the
pins etc. Also manages scheduled tasks (eg. "rtimeout 1800 thermo off" to
execute the command "thermo off" in 30 minutes (1800 seconds).

GPIOmanager uses GPIO-ids, which are different from the pin-ids. For
instance GPIO17 has pin-id 11.

Raspberry Pi Rev1 has slightly different pin allocations. This tool works
correctly with both, but if you are working with a .
"""
import yaml
import time
from os import geteuid
from threading import Thread

# Import either the dummy or the real lib
try:
    import RPi.GPIO as RPiGPIO
    is_dummy_gpio = False

except:
    import dummy
    RPiGPIO = dummy.Dummy()
    is_dummy_gpio = True


# Set this to the revision of your Raspberry Pi (most likely 2)
RASPBERRY_PI_REV = 2

# Map GPIO->PIN
GPIO_TO_PIN_MAP_REV1 = {
    # gpio-id: pin-id,
    0: 3, 1: 5, 4: 7, 7: 26, 8: 24, 9: 21, 10: 19, 11: 23, 14: 8,
    15: 10, 17: 11, 18: 12, 21: 13, 22: 15, 23: 16, 24: 18, 25: 22
}
GPIO_TO_PIN_MAP_REV2 = {
    # gpio-id: pin-id,
    2: 3, 3: 5, 4: 7, 7: 26, 8: 24, 9: 21, 10: 19, 11: 23, 14: 8,
    15: 10, 17: 11, 18: 12, 22: 15, 23: 16, 24: 18, 25: 22, 27: 13
}


# Scheduled command thread
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


# Main GPIO handler class
class GPIO(object):
    INPUT = RPiGPIO.IN
    OUTPUT = RPiGPIO.OUT
    HIGH = RPiGPIO.HIGH
    LOW = RPiGPIO.LOW

    config = None
    commands = None
    async_pool = []
    gpio_pin_map = GPIO_TO_PIN_MAP_REV2

    def __init__(self, logger, configfile):
        self.logger = logger
        self.fn_config = configfile

        # To access the real GPIOs, we need superuser rights
        if not is_dummy_gpio and geteuid() != 0:
            print "Error: gpio-daemon needs to be run as root to access GPIO ports.\n"
            self.logger.error("Error: gpio-daemon needs to be run as root to access GPIO ports.")
            exit(1)

        if RASPBERRY_PI_REV == 1:
            self.gpio_pin_map = GPIO_TO_PIN_MAP_REV1

        self.logger.info("Initializing gpio pins. Using setup for Raspberry Pi Rev%s.", RASPBERRY_PI_REV)

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
        self.logger.info("cmd: '%s'" % cmd)
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
        return self.gpio_pin_map[gpio_id]

    def _reload_config(self):
        self.config = yaml.load(open(self.fn_config))
        self.logger.info("Config loaded: %s", self.config)
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
                self.logger.warn("Error: cannot set mode to '%s' (_gpio_init)", mode)
                return

            # Setup pin to default mode from config file
            self.gpio_setup(gpio_id, mode)

    def _handle_cmd(self, internal_cmd):
        # Internal cmd is the actuall command (triggered by the user command)
        self.logger.info("execute> %s" % internal_cmd)
        cmd_parts = internal_cmd.split(" ")
        cmd = cmd_parts[0]

        if cmd == "set":
            gpio_id, value = cmd_parts[1:3]

            if value == "HIGH":
                value = self.HIGH

            elif value == "LOW":
                value = self.LOW

            else:
                self.logger.warn("Error cannot handle command '%s' due to bad value", internal_cmd)
                return

            self.gpio_output(int(gpio_id), value)

        elif cmd == "rtimeout":
            # Replaceable timeout. Replaces based on "cmd" only.
            timeout = cmd_parts[1]
            cmd = " ".join(cmd_parts[2:])
            self.logger.info("understood rtimeout. cmd in %s seconds: `%s`", timeout, cmd)

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
            self.logger.warn("command '%s' not recognized", cmd)


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
