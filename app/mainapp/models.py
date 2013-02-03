from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    user = models.OneToOneField(User, blank=True, null=True)
    date_created = models.DateTimeField('date created', auto_now_add=True)
    event_type = models.CharField(max_length=50)
    event_value = models.CharField(max_length=50, blank=True, null=True)
    event_info = models.CharField(max_length=50, blank=True, null=True)
    def __unicode__(self):
        return "<Event(%s, %s (-> %s))>" % (self.date_created, self.event_type, self.event_value)
