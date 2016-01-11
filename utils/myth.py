# Utility code for dealing with MythTV.

from myth_to_vid.settings import cfg

def initialize_orphans_list(from_dir=None, filename_pattern=None):
    """
    Reads files matching filename_pattern in from_dir. Presumably,
    these are files created by MythTV and were at one time associated with
    TV recordings. We want a list of files that are still present in that
    directory, but that MythTV no longer "knows" about, probably due to
    a problem with the MythTV backend's database.
    
    For each file that is not associated with a MythTV tv recording
    (that is, for each "orphan,"), constructs an Orphan object and
    saves it in this project's database.
    
    If from_dir or filename_pattern is None, this method will use the defaults
    from the project's configuration.
    
    ASSUMPTIONS:
        * from_dir is on localhost, or mounted via a network fs such as sshfs so
        that it's accessible as if it were on localhost.
    
    """
    pass

def make_video_sample(o):
    """
    o is an Orphan instance. This method
    generates a video sample from the
    original recording file. The sample is
    not only much smaller than the original
    (about 60 or 70 MB, compared to several GB)
    but is in a format that can be reliably viewed
    via HTML 5 in most recent browsers.
    
    ASSUMPTIONS:
        * The host is running Linux or a compatible OS. "Compatible" means, probably,
        Linux or a closely-related OS such as FreeBSD, with a POSIX or near-POSIX
        environment. The code may run successfully on other environments, such as
        a Windows computer with the Cygwin tools installed, but this has not been tested.
        The reason that this is required is that the conversion is done 
        
    """
    pass
    
    pass

class TVRecordingService(object):
    """
    Uses MythTV API calls to get a list of TV recordings for use
    by Orphan-related code. For example, initialize_orphans_list
    needs to check to see if a given filename on a given host
    is in a MythTV tv recording or not.
    
    If it turns out that initialize_orphans_list is the only place
    this is needed, then this will probably be turned into a simple
    get_tv_recordings_list non-class function, as then there will
    be no need to worry about "caching" the list by using a Singleton
    class instance.
    
    Why not build a list once and save it using a Django ORM model,
    as we do with Orphan? Because changes will be made by the
    MythTV backend, and it will be hard to track those changes.
    If it turns out there is a need for it in future, a Django
    model could be used, linked to the MythTV backend's database,
    but this will be more complicated, so we'll skip it for now.
    """
    def __init__(self,hostname=None):
        pass
    
    

