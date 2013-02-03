"""
Deployment with Fabric is super easy. Just push the changes to Github
and run `fab rpi1 deploy`, which will update both the gpio-utils and
the django repository, apply the django db migrations and restart
uwsgi.django.

Commands:

    deploy .............. Update repos, migrate db schemas and restart Django
    upload_settings ..... Upload `settings_production.py`

    restart_django ...... Restart the django uwsgi daemon
    restart_nginx ....... Restart the Nginx daemon
    restart_gpiodaemon .. Restart the GPIO daemon
"""
import os.path
import datetime

from fabric.api import run, local, cd, lcd, put, env, hosts, hide
from fabric.contrib.files import exists

from app.settings import settings_dev
from app.settings import settings_production

HISTFILE = "deployments.log"

# Targets
def rpi1():
    env.use_ssh_config = True
    env.hosts = ["raspberry1_root"]

# Commands
def upload_settings():
    put("app/settings/settings_production.py", "/opt/rpi-django/django/app/settings/settings_production.py")

def restart_django():
    run("/etc/init.d/uwsgi.django restart")

def restart_nginx():
    run("/etc/init.d/nginx restart")

def restart_gpiodaemon():
    run("python2.7 /opt/rpi-django/raspberrypi-gpio-utils/gpio-daemon/gpiodaemon.py restart")

def deploy():
    # Update gpio-utils
    with cd("/opt/rpi-django/raspberrypi-gpio-utils/gpio-daemon"):
        run("git reset --hard")
        run("git pull")

    # Update django project
    with cd("/opt/rpi-django/django"):
        run("git reset --hard")
        run("git pull")

    # Now apply django db migrations
    apps = ["mainapp", "thermostat"]
    with cd("/opt/rpi-django/django/app"):
        for app in apps:
            run("python2.7 manage.py migrate %s" % app)

    # Restart django
    upload_settings()
    restart_django()
    _log("success")

def _log(info, id="deployment"):
    """Log a deployment or rollback"""
    fn = os.path.join(os.path.abspath(os.path.dirname(__file__)), HISTFILE)
    f = open(fn, "a+")
    f.write("%s | %s | %s\n" % (id, datetime.datetime.now(), info))
