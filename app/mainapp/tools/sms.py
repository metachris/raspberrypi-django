import logging
import urllib
import urllib2

from django.conf import settings


log = logging.getLogger(__name__)


def send_sms(to_tel, msg):
    """
        `to_tel` .. should be in international format without + and spaces
                    (eg. 436802425352 or +436802425352)
        `msg` ..... will be properly escaped with urllib. Keep it short!
    """
    to_tel = to_tel.strip().replace(" ", "").replace("-", "").replace("/", "")
    msg = msg.strip()
    log.info("Sending SMS to %s: '%s' (%s chars)" % (to_tel, msg, len(msg)))

    if not settings.SEND_SMS:
        log.info("- disabled by settings.SEND_SMS")
        return

    url = "https://www.intellisoftware.co.uk/smsgateway/sendmsg.aspx"
    values = {'username' : settings.INTELLISENSE_USERNAME,
              'password' : settings.INTELLISENSE_PASSWORD,
              'to' : to_tel,
              'text': msg
    }

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    log.info("- sms response: %s" % the_page)
