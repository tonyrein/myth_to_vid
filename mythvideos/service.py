import configparser
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
        # Read configuration...
        config_file = os.path.join(settings.BASE_DIR, 'mtv_settings.cfg')
        self.cfg = configparser.ConfigParser(interpolation=None)
        config_files_read = self.cfg.read(config_file)
        if len(config_files_read) == 0:
            raise Exception('Could not find config file {}'.format(config_file))
        
    def new_video_from_orphan(self, orphan, target_host=None, delete_orphan=False):
        """
        1. Figures out where to put file based on orphan's title and subtitle -
            creates appropriate subdirectory under target host's top-level
            video directory, if that subdirectory doesn't already exist.
        2. Copies orphan's file to destination subdirectory
        3. Executes MythTV API call to add video by filename and host. This
            results in the addition of a record to MythTV's db table for this video.
        4. Get a MythVideo object corresponding to the new db record.
        5. Set metadata for the MythVideo object, then save it.
        6. If all above was successful and delete_orphan == True, delete the
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
        target_filepath = os.path.join(target_subdir, orphan.filename)
        if not api.add_to_mythvideo(target_filepath, target_host):
			# api call returns False if problem
            raise Exception("Could not add video with filename {} and title {}".format(orphan.filename,orphan.title))
        # Step 4: Get a MythVideo instance for the new entry
        # This call should return only 1 instance...
        newvid = MythVideo.objects.filter(hostname=target_host).filter(filename=target_filepath).get()
        # Step 5: Set metadata and save
        newvid.title = orphan.title
        newvid.subtitle = orphan.subtitle
        newvid.year = orphan.start_date.year
        newvid.length = orphan.duration
        newvid.save()
        # Step 6: Delete original file, if desired
        if delete_orphan:
			os.remove(source_filespec)
			orphan.delete()
        
        
        
        
            
        
