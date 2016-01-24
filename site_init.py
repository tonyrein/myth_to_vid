import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myth_to_vid.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


from orphans.models import Orphan
from utils.myth import initialize_orphans_list, make_video_samples


# Are there any orphans already?

orphan_count = Orphan.objects.count()
if orphan_count > 0:
    init_orphan_list = False
    print("There are already {} orphan records in the database.")
    print("\tDo you want to recreate the list? Doing so will wipe out")
    print("\tall data in the orphan table.")
    print("Type YES (all caps) to wipe out current data and recreate the list, or anything else to keep the current data.")
    user_response = input('Wipe out current data? ')
    if user_response == 'YES':
        init_orphan_list = True
else:
    init_orphan_list = True

if init_orphan_list:
    # Initialize list of Orphan objects:
    num_orphans = initialize_orphans_list(override=True)
    print("Found {} orphan files.".format(num_orphans))
print("Will now make video samples. This may take quite a while (several minutes per file...")
orphan_types, conversion_results = make_video_samples()
#   orphan_types is a dict, with each key pointing to a list. orphan_types = { 'to_do': [], 'empty': [], 'already_there': [] }
#        Each element in those lists is [ type ('empty', 'already_there', or 'to_do'), Orphan object, cmd (for type 'to_do') ] 
#   conversion_results is a list, with one element for each 'to_do' item. Each list consists of
#        [ returnresult from conversion program, error message (if any) from conversion program, filename ]

empty_count = len(orphan_types['empty'])
todo_count = len(conversion_results)
already_there_count = len(orphan_types['already_there'])

print("Results of call to make_video_samples():")
print("Total of {} orphans were processed.".format(empty_count + todo_count + already_there_count))
print("Of these, {} were empty files (zero bytes) and {} already had samples present.".format(empty_count, already_there_count))
print("I attempted to make video samples for the remaining {}.".format(todo_count))
# Each element of res is
#    [ object, cmd, [ returncode, errormessage (if any) ] ]
failures = [ f for f in conversion_results if f[0] != 0 ]
failure_count = len(failures)
success_count = todo_count - failure_count
print("{} attempts succeeded and {} encountered problems.".format(success_count, failure_count))
print("Here are the error messages:")
for f in failures:
    print("{}: {}".format(f[2], f[1].decode('utf-8'))  )
