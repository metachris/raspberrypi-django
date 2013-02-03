from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'mainapp.views.home', name='home'),
    url(r'^thermostat/turn_on$', 'thermostat.views.turn_on', name='thermo_on'),
    url(r'^thermostat/turn_off$', 'thermostat.views.turn_off', name='thermo_off'),
    url(r'^door/unlock', 'mainapp.views.door_unlock', name='door_unlock'),

    # Login and logout url's
    (r'^login/$', 'django.contrib.auth.views.login',
         {'template_name': 'login.html'}),
    (r'^accounts/login/$', 'django.contrib.auth.views.login',
         {'template_name': 'login.html'}),
    url(r'^register/$', 'main.views.register'),
    url(r'^logout/$', 'main.views.logout'),

    # Admin Url's
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
