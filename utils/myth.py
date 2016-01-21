# Utility code for dealing with MythTV.
import configparser
import datetime
from glob import glob
import json
import os.path
import re
from socket import gethostname
import urllib.request



from utils.date_and_time import ensure_tz_aware, ensure_utc, utc_dt_to_local_dt
from orphans.models import Orphan
from django.conf import settings

mythtv_filename_pattern = re.compile('\d{4}_\d{14}\.')
REC_FILENAME_DATE_FORMAT = '%Y%m%d%H%M%S'
BYTES_PER_MINUTE=38928300 # approx. 39 million bytes/minute in a
                            # SD Mythtv recording
                            
def initialize_orphans_list(from_dir=None, filename_pattern=None, override=False):
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
        * no Orphan entries currently exist, or override==True
    
    """
    # Any orphans there yet?
    if Orphan.objects.count() > 0:
        if override == False:
            raise Exception('initialize_orphans_list called with override == False, but Orphans table already has entries')
        else:
            # Dump existing entries...
            Orphan.objects.all().delete()
    # Read configuration...
    config_file = os.path.join(settings.BASE_DIR, 'mtv_settings.cfg')
    cfg = configparser.ConfigParser(interpolation=None)
    config_files_read = cfg.read(config_file)
    if len(config_files_read) == 0:
        raise Exception('Could not find config file {}'.format(config_file))
    
    # Verify running on localhost:
    mythhost = cfg['MYTHTV_CONTENT'].get('MYTHBACKEND')
    if mythhost != gethostname():
        raise Exception('This version must run on MythTV backend - remote host functionality not yet implemented.')
    if from_dir is None:
        from_dir = os.path.join(settings.BASE_DIR, cfg['MYTHTV_CONTENT'].get('TV_RECORDINGS_DIR'))
    if filename_pattern is None:
        filename_pattern = cfg['MYTHTV_CONTENT'].get('RECORDING_FILENAME_PATTERN')
    filespec = os.path.join(from_dir, filename_pattern)
    filelist = [ f for f in glob(filespec) if os.path.isfile(f) ] # don't bother with directories
    if len(filelist) > 0:
        api = MythApi()
        ocounter = 0
        for f in filelist:
            orphandir,fn = os.path.split(f) # split into path and filename
            if not api.is_tv_recording(fn):
                o = Orphan()
                local_dt, channel_id = parse_myth_filename(fn)
                o.start_date = local_dt.date()
                o.start_time = local_dt.time()
                ci = api.get_channel_info(channel_id)
                o.channel_name = ci['ChannelName']
                o.channel_number = ci['ChanNum']
                o.channel_id = channel_id
                o.title = ''
                o.subtitle = ''
                o.filename = fn
                o.directory = orphandir
                o.filesize = os.path.getsize(f)
                o.duration = int(round(o.filesize/BYTES_PER_MINUTE))
                o.hostname = mythhost
                ocounter += 1
                o.save()
        
        return ocounter        
            
    
def parse_myth_filename(filename):
    # Verify filename fits pattern - "\d{4}_\d{14}\."
    # If not, bail out.
    if not mythtv_filename_pattern.match(filename):
        raise Exception('Filename {} does not fit pattern for a MythTV filename.'.format(filename))
    # split filename into components:
    (channel_id,rest) = filename.split('_')
    dt_portion=rest[:14]
    #dt_portion is a timestamp in the format: YYYYMMDDHHMMSS. The
    # timezone is not given in the string, but it is UTC.
    # Make a UTC datetime object from it, then change to local timezone:
    utc_dt = datetime.datetime.strptime(dt_portion,REC_FILENAME_DATE_FORMAT)
    utc_dt = ensure_tz_aware(utc_dt)
    utc_dt = ensure_utc(utc_dt)
    local_dt = utc_dt_to_local_dt(utc_dt)

    return [ local_dt, channel_id ]

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
        The reason that this is required is that the conversion is done using ffmpeg,
        an external program.
        
    """
    pass

# class TVRecordingService(object):
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
#     def __init__(self,hostname=None):
#         if hostname is None:
#             hostname = cfg['MYTHTV_CONTENT'].get('MYTHBACKEND')
#         self.hostname = hostname
#     
#     def is_tv_recording(self, filename):
#         pass


class MythApi(object):
    """
    Wrapper for calls to MythTV API.
    Singleton
    """
    __instance = None
    def __new__(cls, server_name=None, server_port=None):
        """
        Constructor.
        If __instance isn't already there, build it and initialize
        some of its data. Then return it.
        """
        # Read configuration...
        config_file = os.path.join(settings.BASE_DIR, 'mtv_settings.cfg')
        cfg = configparser.ConfigParser(interpolation=None)
        config_files_read = cfg.read(config_file)
        if len(config_files_read) == 0:
            raise Exception('Could not find config file {}'.format(config_file))
        if server_name is None:
            server_name=cfg['MYTHTV_CONTENT'].get('MYTHBACKEND')
        if server_port is None:
            server_port=cfg['MYTHTV_CONTENT'].get('API_PORT')
        if MythApi.__instance is None:
            MythApi.__instance = object.__new__(cls)
            MythApi.__instance.server_name = server_name
            MythApi.__instance.server_port = server_port
            MythApi.__instance._tv_recordings = None # Don't get this unless and until it's needed.
            MythApi.__instance._storage_groups = MythApi.__instance._fill_myth_storage_group_list()
            MythApi.__instance.default_directory = MythApi.__instance.storage_dir_for_name('Default', server_name)
        return MythApi.__instance
    
    """
    This is a property because initializing the list is expensive,
    and this is a simple way to make the initialization "'1013_20140518210000.mpg'lazy."
    """
    @property
    def tv_recordings(self):
        if self._tv_recordings is None:
            self._tv_recordings = self.get_mythtv_recording_list()
        return self._tv_recordings
    
    """
    storage_groups is a property because
         it's read-only.
    """
    @property
    def storage_groups(self):
        return self._storage_groups    
    """
    Make a call to the MythTV API and request JSON back from MythTV server.
    Pass:
      * name of API service
      * name of API call within service
      * data (optional) - a dict of parameters for the call
      * headers (optional)
    Returns:
      * A JSON object built from the data returned from the MythTV server
    Raises:
      * HTTPError
    """
    def _call_myth_api(self,service_name, call_name, data=None, headers={}):
        # Tell server to send back JSON:
        headers['Accept'] = 'application/json'
        
        if data:
            DATA=urllib.parse.urlencode(data)
            DATA=DATA.encode('utf-8')
        else:
            DATA=None
        
        # Assemble url:
        url = (
            "http://{}:{}/{}/{}".format(self.server_name, self.server_port, service_name, call_name)
            )
        # Make a Request object and pass it to the server.
        # Use the returned result to make some JSON to return to our caller
        req = urllib.request.Request(url, data=DATA, headers=headers)
        if DATA:
            req.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        try:
            with urllib.request.urlopen(req) as response:
                the_answer = response.read()
                if the_answer:
                    the_answer = the_answer.decode('utf-8')
                    return json.loads(the_answer)
        except Exception as e:
            return { 'Exception': e.__repr__() }
        
    """
    Gets list of storage groups available to
    MythTV server self.server_name.
     Pass: self
     Return: list, each element of which is a JSON object with the following keys:
       Id,  GroupName,  HostName,  DirName
    """
    def _fill_myth_storage_group_list(self):
        j = self._call_myth_api('Myth', 'GetStorageGroupDirs')
        return j['StorageGroupDirList']['StorageGroupDirs']
    
    """
    Pass: Storage group name and host name
    Return: Disk directory, or None if no match.
    
    """
    def storage_dir_for_name(self, group_name, hostname=None):
        if hostname is None:
            hostname = self.server_name
        for g in self.storage_groups:
            if g['GroupName'] == group_name and g['HostName'] == hostname:
                return g['DirName']
        return None
    
    """
    Pass: Channel id, for example '1008'
    Returns: an ordered dict with the following keys:
    ['@xmlns:xsi', '@version', '@serializerVersion', 'ChanId', 'ChanNum', 'CallSign',
     'IconURL', 'ChannelName', 'MplexId', 'TransportId', 'ServiceId', 'NetworkId',
      'ATSCMajorChan', 'ATSCMinorChan', 'Format', 'Modulation', 'Frequency', 'FrequencyId',
       'FrequencyTable', 'FineTune', 'SIStandard', 'ChanFilters', 'SourceId', 'InputId',
        'CommFree', 'UseEIT', 'Visible', 'XMLTVID', 'DefaultAuth', 'Programs']
    This assumes that a valid channel id is passed. If the channel id is invalid, the
    api call will return an exception code.
    """
    def get_channel_info(self,channel_id):
        res_dict = self._call_myth_api('Channel', 'GetChannelInfo',
                 { 'ChanID': channel_id } )
        if 'Exception' in res_dict:
            raise Exception("Problem getting channel info for channel {}: {}".format(channel_id, res_dict['Exception']))
        else:
            return res_dict['ChannelInfo']
    
    """
    Queries the MythAPI server for a list of the tv recordings.
    Pass: nothing
    Return: a list, each element of which is an ordereddict with the following keys:
       StartTime, EndTime, Title, SubTitle, Category, CatType, Repeat, VideoProps,
       AudioProps, SubProps, SeriesId, ProgramId, Stars, FileSize, LastModified, ProgramFlags,
       FileName, HostName, Airdate, Description, Inetref, Season, Episode, Channel,
       Recording, Artwork,
       FileSpec, Duration
       Note that the values for several of these keys (Channel, Recording, Artwork) are
       ordereddicts in turn.
       For Channel, the keys are:
           ChanId,  ChanNum,  CallSign,  IconURL,  ChannelName,  MplexId,  TransportId,  ServiceId,
            NetworkId,  ATSCMajorChan,  ATSCMinorChan,  Format,  Modulation,  Frequency,  FrequencyId,
             FrequencyTable,  FineTune,  SIStandard,  ChanFilters,  SourceId,  InputId,  CommFree,
              UseEIT,  Visible,  XMLTVID,  DefaultAuth,  Programs
      For Recording, the keys are:
        Status,  Priority,  StartTs,  EndTs,  RecordId,  RecGroup,  PlayGroup,  StorageGroup,  RecType,  DupInType,  DupMethod,  EncoderId,  Profile
      For Artwork, the one key is:
        ArtworkInfos
        
      
      
      The 'StartTs' and 'EndTs' fields are used to calculate the duration -- these represent the
      actual start and end times of the recording; the fields 'StartTime' and 'EndTime' are the
      scheduled times, and do not reflect the fact that the recording may have started and/or
      ended at other than the scheduled times.
      
    """
    def get_mythtv_recording_list(self):
        res_dict = self._call_myth_api('Dvr', 'GetRecordedList')
        if 'Exception' in res_dict:
            raise Exception("Problem getting MythTV recording list: {}".format(res_dict['Exception']))
        else:
            return res_dict['ProgramList']['Programs']
    
    
    def is_tv_recording(self,filename):
        """
        Is this filename associated with a MythTV tv recording?
        """
        m = [ p for p in self.tv_recordings if p['FileName'] == filename ]
        return len(m) > 0
