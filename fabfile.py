"""
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
    run("kill -9 `cat /tmp/uwsgi-django.pid`")
    run("uwsgi --ini /opt/rpi-django/django/app/uwsgi.ini")

def deploy():
    with cd("/opt/rpi-django/django"):
        run("git reset --hard")
        run("git pull")

    #restart_django()
    _log("success")

def _log(info, id="deployment"):
    """Log a deployment or rollback"""
    fn = os.path.join(os.path.abspath(os.path.dirname(__file__)), HISTFILE)
    f = open(fn, "a+")
    f.write("%s | %s | %s\n" % (id, datetime.datetime.now(), info))
