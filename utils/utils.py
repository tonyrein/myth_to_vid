import paramiko
from settings import cfg

def make_ssh_client(hostname):
    ssh_configs = cfg['SSH_CONFIGS'] # raises KeyError if section does not exist.
    
    conf = ssh_configs[hostname] # raises KeyError if key does not exist
    user,pword,port = conf.split(',')
    port = int(port)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname, username=user,password=pword,port=port,
        allow_agent=False, look_for_keys=False
        )
    return ssh_client


"""
Execute a stat command on the remote host and
parse the output into a dict to return.

Pass:
    * hostname
    * filespec -- either a directory, a file name or pattern, or a combination
    * fields -- a list of strings representing the desired information about
    the filespec. For example: [ 'size','name','owner_id','group_id' ] would
    be asking for the file's size (in bytes) and name, and for its owner's and
    group's ids.
    
Return:
   * a list of dict. In the above example, the values for one list entry might be:
       { 'size': '12743', 'name': '/mnt/store/foo.txt', 'owner_id': '1001', 'group_id': '1020' }
    Note that all values returned are strings.
    
The fields which can be specified are:
    name
    size (this asks for the size in bytes)
    blocks (this asks for the number of blocks the file uses)
    bytes_per_block
    owner_name
    owner_id
    group_name
    group_id
    creation_time (in seconds since epoch. 0 if unknown)
    permissions (in octal)
    
"""
def stat_remote_host(hostname, filespec, fields):
    # a dict allowing lookup of stat command's
    # option symbol for field names:
    allowed_fields = {
        'name':'%n',
        'size':'%s',
        'blocks':'%b',
        'bytes_per_block':'%B',
        'owner_name':'%U',
        'owner_id':'%u',
        'group_name':'%G',
        'group_id':'%g',
        'creation_time':'%W',
        'permissions':'%a',
        'type':'%F',
    }
    delimiter='@#$' # Unlikely (we hope) to occur in expected field values
    fields_requested = ''
    for f in fields:
        if not f in allowed_fields:
            raise Exception("Invalid field: {}".format(f))
        fields_requested += allowed_fields[f] + delimiter
    stat_cmd = 'stat -c {} {}'.format(fields_requested,filespec)
    cl=make_ssh_client(hostname)
    stdin,stdout,stderr=cl.exec_command(stat_cmd)
    for l in stderr.readlines():
        print(l)
    ret_list=[]
    for line in stdout.readlines():
        line = line.strip()
        line = line.rstrip(delimiter)
        d = {}
        fs = line.split(delimiter)
        for i in range(len(fs)):
            d[fields[i]] = fs[i]
        ret_list.append(d)
    return ret_list
        
def size_remote_file(hostname, filespec):
    res_list = stat_remote_host(hostname, filespec, ['size'])
    if not res_list or len(res_list) == 0:
        raise Exception("{} not found on host {}".format(filespec,hostname))
    if not 'size' in res_list[0]:
        raise Exception("Could not determine size of {} on host {}".format(filespec,hostname))
    return int(res_list[0]['size'])
