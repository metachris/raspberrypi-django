"""
"""
import os.path
import datetime

from fabric.api import run, local, cd, lcd, put, env, hosts, hide
from fabric.contrib.files import exists

from app.settings import settings_dev
from app.settings import settings_production

HISTFILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "deployments.log")

# Helper for later
NOW = datetime.datetime.now()
NOW_DATE_STR = NOW.strftime("%Y-%m-%d")

# Targets
def rpi1():
    env.use_ssh_config = True
    env.hosts = ["raspberry1"]


# Commands
def _upload():
    local("sh build.sh")
    put("/tmp/raspberry-django-deploy/pack.tar.gz", "/opt/rpi-django/")
    with cd("/opt/rpi-django/"):
        run("tar -xvf pack.tar.gz")
        run("rm pack.tar.gz")
    local("rm -rf /tmp/raspberry-django-deploy")


def restart_django():
    run("kill -9 `cat /tmp/uwsgi-django.pid`")
    run("uwsgi --ini /opt/rpi-django/django/app/uwsgi.ini")


def deploy():
    _upload()
    restart_django()
    _log("success")


def _log(info, id="deployment"):
    """Log a deployment or rollback"""
    f = open(HISTFILE, "a+")
    f.write("%s | %s | %s\n" % (id, datetime.datetime.now(), info))
