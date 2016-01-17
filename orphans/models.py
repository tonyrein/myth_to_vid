import os.path

from django.core.urlresolvers import reverse
from django.db import models

# Create your models here.

class Orphan(models.Model):
    intid = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=128)
    title = models.CharField(max_length=128, blank=True, default='')
    directory = models.CharField(max_length=256)
    filename = models.CharField(max_length=20)
    filesize = models.BigIntegerField(blank=True, default=0)
    duration = models.SmallIntegerField(blank=True, default=0)
    start_date = models.DateField()
    start_time = models.TimeField()
    subtitle = models.TextField(blank=True, default='')
    channel_id = models.CharField(max_length=4)
    channel_number = models.SmallIntegerField()
    channel_name = models.CharField(max_length=256)
    
     
    @property
    def samplename(self): #"Calculated" field -- name of sample file
        return os.path.splitext(self.filename)[0] + '.ogv'
    @classmethod
    def db_name(cls):
        return 'default'
 
     
    def get_absolute_url(self):
        return reverse('orphans:OrphanDetailView', args=[str(self.intid)])
    
    class Meta:
        managed = True
        db_table = 'orphans'
        # The combination of hostname and filename must be unique. This will be enforced both by model
        # validation and at the database level. If an attempt is made to save a model item which violates
        # this contraint, a django.db.IntegrityError will be raised.
        unique_together = ('hostname', 'filename')
