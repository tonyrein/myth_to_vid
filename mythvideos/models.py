
from django.db import models
"""   
   One issue is that MySQL/MariaDB don't store the timezone in date/time fields.
   Therefore, if your Django site has "USE_TZ=True," you get a warning about "naive"
   datetime values when you save a Video object back to the database.
   To get around this, it's necessary to convert the datetime value into a timezone-
   aware datetime before saving, by doing something like:
   
   (assume "v" is a MythVideo object)
   
   from django.utils import timezone
   import pytz
   d = v.insertdate
   timezone.make_aware(d,pytz.timezone('UTC')
   v.insertdate = d
"""
class MythVideo(models.Model):
    @classmethod
    def db_name(cls):
        return 'mythtv'
    
    intid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    subtitle = models.TextField()
    tagline = models.CharField(max_length=255, blank=True, null=True)
    director = models.CharField(max_length=128)
    studio = models.CharField(max_length=128, blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    rating = models.CharField(max_length=128)
    inetref = models.CharField(max_length=255)
    collectionref = models.IntegerField()
    homepage = models.TextField()
    year = models.IntegerField()
    releasedate = models.DateField()
    userrating = models.FloatField()
    length = models.IntegerField()
    playcount = models.IntegerField()
    season = models.SmallIntegerField()
    episode = models.SmallIntegerField()
    showlevel = models.IntegerField()
    filename = models.TextField()
    hash = models.CharField(max_length=128)
    coverfile = models.TextField()
    childid = models.IntegerField()
    browse = models.IntegerField()
    watched = models.IntegerField()
    processed = models.IntegerField()
    playcommand = models.CharField(max_length=255, blank=True, null=True)
    category = models.IntegerField()
    trailer = models.TextField(blank=True, null=True)
    host = models.TextField()
    screenshot = models.TextField(blank=True, null=True)
    banner = models.TextField(blank=True, null=True)
    fanart = models.TextField(blank=True, null=True)
    insertdate = models.DateTimeField(blank=True, null=True)
    contenttype = models.CharField(max_length=43)
    
    class Meta:
        managed = False
        db_table = 'videometadata'
