import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myth_to_vid.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


from orphans.models import Orphan
from utils.myth import initialize_orphans_list, VideoSampleMaker


# Are there any orphans already?

original_orphan_count = Orphan.objects.count()
if original_orphan_count > 0:
    init_orphan_list = False
    print("There are already {} orphan records in the database.".format(original_orphan_count))
    print("\tDo you want to recreate the list? Doing so will wipe out")
    print("\tall data in the orphan table.")
    print("Type YES (all caps) to wipe out current data and recreate the list, or anything else to keep the current data.")
    user_response = input('Wipe out current data? --> ')
    if user_response == 'YES':
        init_orphan_list = True
else:
    init_orphan_list = True

if init_orphan_list:
    # Initialize list of Orphan objects:
    num_orphans = initialize_orphans_list(override=True)
    print("Found {} orphan files.".format(num_orphans))
else:
    num_orphans = original_orphan_count
    
if num_orphans > 0:
    print("There are {} records in the orphans database table.".format(num_orphans))
    print("\tChecking whether any of them need video previews made...")
    vm = VideoSampleMaker()
    print("\nA total of {} orphans were checked.".format(vm.empty_count + vm.to_do_count + vm.already_there_count))
    print("Of these, {} were empty files (zero bytes) and {} already had samples present.".format(vm.empty_count, vm.already_there_count))
    if vm.to_do_count > 0:
        print("I will attempt to make video samples for the remaining {}...".format(vm.to_do_count))
        print("\tThis will take several minutes per file...")
        conversion_results = vm.make_video_samples()
        # Each element of conversion_results is [ returncode, error message (if any), filename ]
        failures = [ f for f in conversion_results if f[0] != 0 ]
        failure_count = len(failures)
        success_count = vm.to_do_count - failure_count
        print("{} attempts succeeded and {} encountered problems.".format(success_count, failure_count))
        if failure_count > 0:
            print("Here are the error messages:")
            for f in failures:
                print("{}: {}".format(f[2], f[1].decode('utf-8'))  )
    else:
        print("There were no orphan records which needed samples made.")
        
else: # num_orphans not > 0
    print("No orphan records to process -- exiting.")