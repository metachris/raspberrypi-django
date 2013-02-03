The goal of this project is to get Django running on the Raspberry Pi and serve it via Nginx and UWSGI over port 80. Deployment
to the RPi is done via Fabric. Incorporates goodies from [django-boilerplate](https://github.com/metachris/django-boilerplate)
and [photoblog](https://github.com/metachris/photoblog).


Quick Start / Tutorial
======================
Raspberry Initial Setup
-----------------------
* Download SD card image and boot for 1st time; change settings as needed
* Setup OpenSSH, update system
* Wifi Setup

Time to install some tools:

    $ sudo apt-get screen htop git
    $ sudo apt-get install python-rpi.gpio


Nginx Webserver Setup
---------------------
http://nginx.org/

    $ sudo apt-get install nginx
    $ sudo /etc/init.d/nginx start

Now visit `http://[RaspberryPi-IP]` with your browser


UWSGI Setup
-----------

    # sudo apt-get install uwsgi uwsgi-plugin-python



DEV Desktop/Laptop Setup
========================
The following setup is for your development machine:

Get Pip
-------
    $ apt-get install python-setuptools && easy_install-2.7 pip

or

    $ curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    $ sudo python get-pip.py


Get VirtualEnv
--------------

    $ pip install virtualenv


Django App Setup
----------------
https://github.com/metachris/django-boilerplate

    $ cd /var
    $ sudo mkdir www
    $ sudo chown chris:chris www
    $ cd www
    $ git clone https://github.com/metachris/django-boilerplate.git <YOUR_PROJECT_DIR> (we use /var/www/django)
    $ cd django
    $ virtualenv env
    $ . env/bin/activate
    $ pip install -r dependencies.txt

    # Setting up Twitter Bootstrap
    $ git submodule init
    $ git submodule update

    # Build bootstrap for the first time
    $ cd app/static/twitter-bootstrap
    $ make bootstrap


Customize Django
----------------

1. Edit the settings
2. Create the DB and make the initial migration with (South)[http://south.readthedocs.org/en/latest/tutorial/part1.html]:

	$ python manage.py syncdb
	$ python manage.py schemamigration <APPNAME> --initial
	$ python manage.py migrate <APPNAME>

For all subsequent migrations use the following commands:

    $ python manage.py schemamigration <APPNAME> --auto
    $ python manage.py migrate <APPNAME>
