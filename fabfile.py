"""
"""
import os.path
import datetime

from fabric.api import run, local, cd, lcd, put, env, hosts, hide
from fabric.contrib.files import exists

from app.settings import settings_dev
from app.settings import settings_production


# Deployments log file (in same path as fabfile)
HISTFILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "deployments.log")

# Helper for later
NOW = datetime.datetime.now()
NOW_DATE_STR = NOW.strftime("%Y-%m-%d")


# Environments
def raspberry1():
    "Set production target"
    env.use_ssh_config = True
    env.hosts = ["raspberry1"]


def upload():
    #rpi1()
    # Pack dir with tar
    local("sh build.sh")
    put("/tmp/rp1dpl/pack.tar.gz", "/opt/rpi-django/")
    with cd("/opt/rpi-django/"):
        run("tar -xvf pack.tar.gz")
        run("rm pack.tar.gz")

def restart_django():
    run("kill -9 `cat /tmp/uwsgi-django.pid")
    run("uwsgi --ini /opt/rpi-django/django/app/uwsgi.ini")
#    """Upload files not in git (from list in code)"""
#    upload_settings()
#    files = ["app/templates/analytics_snippet.html"]
#    for fn in files:
#        fn_from = os.path.join(env.dir_local, fn)
#        fn_to = os.path.join(env.dir_remote, fn)
#        put(fn_from, fn_to)

