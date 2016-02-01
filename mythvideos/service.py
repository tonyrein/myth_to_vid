import configparser
import datetime
import iso8601
import os
import os.path
import socket
import shutil

from django.conf import settings

from mythvideos.models import MythVideo
from orphans.models import Orphan
from utils.myth import MythApi


"""
Code to manipulate MythVideo database entries (via mythvideo.models) and
data processed via MythTV API calls, and to coordinate between the two
types of entities.
"""
class MythVideoService(object):
    def __init__(self):
        self.api = MythApi()
    
    def activate_video(self, data={}):
        """
        data is a dict, with the following fields:
            * filespec - mandatory. This field also may include a subdirectory portion.
                That is, if the file's name is "123.mpg" and it's in the "History" subdirectory
                under the top-level video directory, then the filespec would be "History/123.mpg"
                In the above example, if the video top-level directory was "/mnt/store/mythtv/videos"
                then the full path to this file would be "/mnt/store/mythtv/videos/History/123.mpg"
                You would put only "History/123.mpg" in this field.
            * hostname - optional. If none is supplied, then the default value from the config file
                will be used.
            * title - optional. If none is supplied, then the filespec will be used, minus the extension
                and with underlines converted to spaces and path separation characters ("/" or "\") converted
                to ": " For example, "History/Elizabeth_I_and_Shakespeare.mpg" would be converted to
                "History: Elizabeth I and Shakespeare"
            * subtitle - optional. If none is supplied, then the filespec will be used, minus the extension
                and with underlines converted to spaces and path separation characters ("/" or "\") converted
                to ": " For example, "History/Elizabeth_I_and_Shakespeare.mpg" would be converted to
                "History: Elizabeth I and Shakespeare"
            * length - optional. This is the duration of the video, in minutes. If none is supplied,
                then this will be set to 0.
                An exception will be thrown if the value of this field cannot be cast to an integer.
            * releasedate - optional. If none is supplied, then this will be set to January 1, 1970. If
                supplied, then this should be a string in ISO8601 format, for example:
                "2015-11-28T00:00:00Z"
                An exception will be thrown if this field is not in the valid format.
            * contenttype - optional. If none is supplied, then this will be set by the database
                back end to the table's default for this field. If supplied, then this must be one
                of the values 'MOVIE', 'TELEVISION', 'ADULT', 'MUSICVIDEO', or 'HOMEVIDEO'
                
        Returns:
            MythVideo object, or None if there was a failure adding the file.
        """
        print(data)
        filespec = data.get('filespec', None)
        if filespec is None or filespec == '':
            raise ValueError("You must supply the filename of the video to activate.")
        # If no hostname supplied, use default from api...
        hostname = data.get('hostname', self.api.server_name)
        # Is this video already in the collection?
        VL = MythVideo.objects.filter(filename=filespec) # returns a list
        if len(VL) > 0: # The list has at least one member
            v = VL[0]
        else: # Not already there -- add it
        # Use MythTV API call to tell MythTV server to add a record to its db for this file...
            res = self.api.add_to_mythvideo(filespec, hostname) # returns True on success
            if not res:
                raise Exception("Could not add video {}".format(filespec))
            v = MythVideo.objects.filter(filename=filespec).get() # This will throw an exception if still not there
        # Now that we have our MythVideo object, fill in its fields...
        v.title = data.get('title', None)
        if not v.title:
            v.title = os.path.splitext(v.filename)[0].replace('_',' ').replace(os.sep,": ")
        print("Title: {}".format(v.title))
        v.subtitle = data.get('subtitle', None)
        if not v.subtitle:
            v.subtitle = os.path.splitext(v.filename)[0].replace('_',' ').replace(os.sep,": ")
        print("SubTitle: {}".format(v.subtitle))
        v.length = int(data.get('length', 0))
        ct = data.get('contenttype', None)
        if ct:
            v.contenttype = ct
        datestring = data.get('releasedate', None)
        if datestring:
            v.releasedate = iso8601.parse_date(datestring)
        else:
            v.releasedate = datetime.datetime(1970,1,1)
        print(v.releasedate)
        v.year = v.releasedate.year
        v.save()
        return v
                

            
        
            
    def new_video_from_orphan(self, orphan, target_host=None, delete_orphan=False):
        """
        1. Figures out where to put file based on orphan's title and subtitle -
            creates appropriate subdirectory under target host's top-level
            video directory, if that subdirectory doesn't already exist.
        2. Copies orphan's file to destination subdirectory
        3. Calls activate_video()
        4. If all above was successful and delete_orphan == True, delete the
            orphan's disk file and the Orphan ORM instance.
        """
        # Step 1: Derive source and target. Create target directory, if needed.
        api = MythApi()
        if target_host is None:
            target_host = api.server_name
        if target_host != socket.gethostname():
            raise Exception("Sorry - cross-host file moves not yet implemented.")
        
        if orphan.title is None or orphan.title == '':
            raise Exception("You must supply a title for the orphaned recording.")
        target_top_level_dir = api.videos_directory
        target_subdir = orphan.title.replace(' ','_')
        source_dir = api.default_directory
        source_filespec = os.path.join(source_dir,orphan.filename)
        target_directory = os.path.join(target_top_level_dir, target_subdir)
        os.makedirs(target_directory, exist_ok=True)
        # Step 2: Copy file
        shutil.copy2(source_filespec, target_directory, follow_symlinks=True)
        # Step 3: Call MythTV API to add video
        # Construct data dict to pass to activate_video:
        target_filepath = os.path.join(target_subdir, orphan.filename)
        data = {
                'filespec': target_filepath,
                'hostname': target_host,
                'title': orphan.title,
                'subtitle': orphan.subtitle,
                'releasedate': orphan.start_date.isoformat(),
                'length': orphan.duration, # this value is an integer, in minutes
                }
        v = self.activate_video(data)
        # Step 6: Delete orphan, if desired, but only if activation went OK
        if delete_orphan and v is not None:
            os.remove(source_filespec)
            orphan.delete()
        return v
        
        
        
        
            
        
