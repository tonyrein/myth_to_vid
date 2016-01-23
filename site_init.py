import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myth_to_vid.settings'
import django

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


# Initialize list of Orphan objects:
from utils.myth import initialize_orphans_list, make_video_samples
num_orphans = initialize_orphans_list(override=True)
print("Found {} orphan files.".format(num_orphans))
print("Will now make video samples...")
res = make_video_samples()
empty_count = len(res['empty'])
todo_count = len(res['to_do'])
already_there_count = len(res['already_there'])

print("Results of call to make_video_samples():")
print("Total of {} orphans were processed.".format(empty_count + todo_count + already_there_count))
print("Of these, {} were empty files (zero bytes) and {} already had samples present.".format(empty_count, already_there_count))
print("I attempted to make video samples for the remaining {}.".format(todo_count))
# success_stories = [ t for t in res['to_do'] if t[0] == 0 ]
failures = [ t for t in res['to_do'] if t[0] != 0 ]
failure_count = len(failures)
success_count = todo_count - failure_count
print("{} attempts succeeded and {} encountered problems.".format(success_count, failure_count))
print("Here are the error messages:")
for f in failures:
    print(f[1].decode('utf-8'))
