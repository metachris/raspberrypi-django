"""
Manages communication with GPIO and receiving commands

RPi.GPIO works with pin-ids instead of GPIO-ids (for instance GPIO17 has pin-id 11)
"""
import yaml

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


class GPIO(object):
    INPUT = RPiGPIO.IN
    OUTPUT = RPiGPIO.OUT
    HIGH = RPiGPIO.HIGH
    LOW = RPiGPIO.LOW

    config = None
    commands = None

    def __init__(self):
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
            self._handle_cmd(self.commands[cmd])
        else:
            print "- not found"

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
        RPiGPIO.setmode(RPiGPIO.BOARD)
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
        cmd, gpio_id, value = internal_cmd.split(" ")[:3]
        if cmd == "set":
            if value == "HIGH":
                value = self.HIGH
            elif value == "LOW":
                value = self.LOW
            else:
                print "Error cannot handle command '%s' due to bad value" % internal_cmd
                return

            self.gpio_output(int(gpio_id), value)



if __name__ == "__main__":
    g = GPIO()
    g.handle_cmd("thermo on")
    g.cleanup()
