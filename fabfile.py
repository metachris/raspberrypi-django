"""
"""
import os.path
import datetime

from fabric.api import run, local, cd, lcd, put, env, hosts, hide
from fabric.contrib.files import exists

from app.settings import settings_dev
from app.settings import settings_production

HOSTS = ["raspberry1"]
HISTFILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "deployments.log")

# Helper for later
NOW = datetime.datetime.now()
NOW_DATE_STR = NOW.strftime("%Y-%m-%d")


def _upload():
    local("sh build.sh")
    put("/tmp/raspberry-django-deploy/pack.tar.gz", "/opt/rpi-django/")
    with cd("/opt/rpi-django/"):
        run("tar -xvf pack.tar.gz")
        run("rm pack.tar.gz")
    local("rm -rf /tmp/raspberry-django-deploy")


def _restart_django():
    run("kill -9 `cat /tmp/uwsgi-django.pid`")
    run("uwsgi --ini /opt/rpi-django/django/app/uwsgi.ini")


def deploy():
    env.use_ssh_config = True
    env.hosts = HOSTS
    _upload()
    _restart_django()
    _log("success")


def _log(info, id="deployment"):
    """Log a deployment or rollback"""
    f = open(HISTFILE, "a+")
    f.write("%s | %s | %s\n" % (id, datetime.datetime.now(), info))
