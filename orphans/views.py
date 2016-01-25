import os
import os.path
import socket

from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.template import defaultfilters
from django.views.generic import DeleteView, DetailView, UpdateView 

import django_tables2 as djt2
from django_tables2 import  SingleTableView
from django_tables2.utils import A  # alias for Accessor


from orphans.models import Orphan

# Create your views here.

# table to use when displaying OrphanList
class OrphanListTable(djt2.Table):
#     play = djt2.LinkColumn('orphans:OrphanUpdateView', text='Edit Entry', args=[ A('intid')], attrs={ 'target': '_blank' }, empty_values=(), orderable=False )
    play = djt2.LinkColumn('orphans:OrphanUpdateView', text='Edit Entry', args=[ A('intid')], empty_values=(), orderable=False )
    samplename = djt2.Column()
    # Format filesize and time columns
    def render_filesize(self,value):
        return defaultfilters.filesizeformat(value)
    def render_start_date(self,value):
        return defaultfilters.date(value, 'D, m/d/Y')
    def render_start_time(self,value):
        return defaultfilters.time(value, 'h:i A')
    class Meta:
        model = Orphan
        attrs = { 'class': 'paleblue' }
        exclude = ('samplename','intid', 'channel_id','filename','hostname','directory')
        sequence = ('play','channel_number', 'channel_name', 'start_date', 'start_time','filesize','duration','title','subtitle')
# DeleteView
class OrphanListView(SingleTableView):
    model = Orphan
    table_class = OrphanListTable

class OrphanUpdateView(UpdateView):
    model = Orphan
    readonly_fields = [ 'start_date','start_time','channel_number','channel_name','duration','filesize','samplename'  ]
    fields = [ 'title','subtitle']

class OrphanDetailView(DetailView):
    model = Orphan

class OrphanDeleteView(DeleteView):
    """
    Deletes the file associated with the Orphan object,
    then deletes the Orphan object.
    
    Assumes that the file is on localhost.
    """
    model = Orphan
    success_url = reverse_lazy('orphans:OrphanListView')
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.hostname != socket.gethostname():
            raise Exception("This version of this method requires that it be running on the same host as the recording file is found on.")
        print("About to delete Orphan {}.".format(self.object.intid))
        print("Filename: {}".format(self.object.filename))
        print("Directory: {}".format(self.object.directory))
        print("Hostname: {}".format(socket.gethostname()))
        print("Orphan's host name: {}".format(self.object.hostname))
        filespec = os.path.join(self.object.directory,self.object.filename)
        os.remove(filespec)
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())
        