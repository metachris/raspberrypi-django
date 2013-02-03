import datetime

from django.http import  HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth

import mainapp.models as models
import mainapp.tools.gpio

# Global gpio-client which keeps an open connection
# and can send data to the gpio daemon at any point in time.
gpio_client = mainapp.tools.gpio.GPIOClient().connect()

# Views start here
def home(request):
    # Prepare heating info (current state and log)
    last_events_thermo = models.Event.objects.filter(event_type="thermo").order_by("-date_created")[:5]
    is_thermo_on = False
    thermo_time_since_last_on_mins = None
    if len(last_events_thermo):
        last_event = last_events_thermo[0]
        if last_event.event_value == "on":
            off = last_event.date_created + datetime.timedelta(minutes=30)
            is_thermo_on = off > datetime.datetime.now()
            time_since_last_on = off - datetime.datetime.now()
            time_since_last_on_secs = time_since_last_on.total_seconds()
            thermo_time_since_last_on_mins = int(time_since_last_on_secs / 60) + 1

    # Prepare door log
    last_events_door = models.Event.objects.filter(event_type="door").order_by("-date_created")[:5]

    # Render
    return render(request, 'index.html', { "thermo_lastevents": last_events_thermo,
                                           "thermo_is_heating": is_thermo_on,
                                           "thermo_time_since_last_on_mins": thermo_time_since_last_on_mins,
                                           "last_events_door": last_events_door })


def door_unlock(request):
    gpio_client.send("door unlock")
    gpio_client.send("rtimeout 5 door lock")
    event = mainapp.models.Event(event_type="door", event_value="unlock")
    event.save()
    return HttpResponseRedirect("/")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
