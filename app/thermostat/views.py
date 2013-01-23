import time
import threading

from django.http import  HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth

import models
import tools.gpio

def home(request):
    last_events = models.ThermoSwitchEvent.objects.all().order_by("-date_created")[:5]
    return render(request, 'index.html', { "thermo_lastevents": last_events })


class TurnOffThread(threading.Thread):
    is_cancelled = False

    def __init__(self, timeout_sec=1):
        threading.Thread.__init__(self)
        self.timeout_sec = timeout_sec

    def run(self):
        time.sleep(self.timeout_sec)
        if self.is_cancelled:
            pass


def log_event(is_on):
    event = models.ThermoSwitchEvent(is_on=is_on)
    event.save()
    print event


def turn_on(request):
    tools.gpio.send_to_gpio_daemon("thermo on")
    log_event(True)
    return HttpResponseRedirect("/")


def turn_off(request):
    tools.gpio.send_to_gpio_daemon("thermo off")
    log_event(False)
    return HttpResponseRedirect("/")

