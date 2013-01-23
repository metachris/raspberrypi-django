import datetime

from django.http import  HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth

import models
import tools.gpio


def home(request):
    last_events = models.ThermoSwitchEvent.objects.all().order_by("-date_created")[:5]

    is_heating = False
    last_event = last_events[0]
    time_since_last_on_mins = None
    if last_event.is_on:
        off = last_event.date_created + datetime.timedelta(minutes=30)
        is_heating = off > datetime.datetime.now()
        time_since_last_on = off - datetime.datetime.now()
        time_since_last_on_secs = time_since_last_on.total_seconds()
        time_since_last_on_mins = int(time_since_last_on_secs / 60) + 1

    return render(request, 'index.html', { "thermo_lastevents": last_events,
            "thermo_is_heating": is_heating,
            "thermo_time_since_last_on_mins": time_since_last_on_mins })


def turn_on(request):
    tools.gpio.send_to_gpio_daemon("thermo on")
    event = models.ThermoSwitchEvent(is_on=True)
    event.save()
    return HttpResponseRedirect("/")


def turn_off(request):
    tools.gpio.send_to_gpio_daemon("thermo off")
    event = models.ThermoSwitchEvent(is_on=False)
    event.save()
    return HttpResponseRedirect("/")

