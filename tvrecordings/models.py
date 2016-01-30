from django.db import models

# Create your models here.
class TvRecording(models.Model):
    intid = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=128)
    title = models.CharField(max_length=128, blank=True, default='')
    directory = models.CharField(max_length=256)
    filename = models.CharField(max_length=20)
    filesize = models.BigIntegerField(blank=True, default=0)
    duration = models.SmallIntegerField(blank=True, default=0)
    start_utc_datetime = models.DateTimeField()
    subtitle = models.TextField(blank=True, default='')
    channel_id = models.CharField(max_length=4)
    channel_number = models.SmallIntegerField()
    channel_name = models.CharField(max_length=256)
    
     
    @classmethod
    def db_name(cls):
        return 'default'
 
     
    class Meta:
        managed = True
        db_table = 'tvrecordings'
        # The combination of hostname and filename must be unique. This will be enforced both by model
        # validation and at the database level. If an attempt is made to save a model item which violates
        # this contraint, a django.db.IntegrityError will be raised.
        unique_together = ('channel_id', 'start_utc_datetime')
