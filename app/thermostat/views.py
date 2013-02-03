import datetime

from django.http import  HttpResponseRedirect
from django.shortcuts import render

import mainapp.models
import mainapp.tools.gpio

# Global gpio-client which keeps an open connection
# and can send data to the gpio daemon at any point in time.
gpio_client = mainapp.tools.gpio.GPIOClient().connect()

# Views start here
def turn_off(request):
    gpio_client.send("thermo off")
    event = mainapp.models.Event(event_type="thermo", event_value="off")
    event.save()
    return HttpResponseRedirect("/")


def turn_on(request):
    gpio_client.send("thermo on")
    gpio_client.send("rtimeout 1800 thermo off")
    event = mainapp.models.Event(event_type="thermo", event_value="on")
    event.save()
    return HttpResponseRedirect("/")
