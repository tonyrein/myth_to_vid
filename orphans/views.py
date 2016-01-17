from django.shortcuts import render
from django.http import HttpResponse
from django.template import defaultfilters
from django.views.generic import ListView, UpdateView
from django.views.generic.detail import DetailView

import django_tables2 as djt2
from django_tables2 import  SingleTableView
from django_tables2.utils import Accessor, A  # alias for Accessor


from orphans.models import Orphan

# Create your views here.

# class OrphanListView(ListView):
#     model = Orphan


# table to use when displaying OrphanList
class OrphanListTable(djt2.Table):
    play = djt2.LinkColumn('orphans:OrphanUpdateView', text='Edit Entry', args=[ A('intid')], attrs={ 'target': '_blank' }, empty_values=(), orderable=False )
    samplename = djt2.Column()
    # Format filesize and time columns
    def render_filesize(self,value):
        return defaultfilters.filesizeformat(value)
    def render_start_time(self,value):
        return defaultfilters.time(value, 'h:i A')
    class Meta:
        model = Orphan
        attrs = { 'class': 'paleblue' }
        exclude = ('samplename','intid', 'channel_id','filename','hostname','directory')
        sequence = ('play','channel_number', 'channel_name', 'start_date', 'start_time','filesize','duration','title','subtitle')

class OrphanListView(SingleTableView):
    model = Orphan
    table_class = OrphanListTable

class OrphanUpdateView(UpdateView):
    model = Orphan
    readonly_fields = [ 'start_date','start_time','channel_number','channel_name','duration','filesize','samplename'  ]
    fields = [ 'title','subtitle']

class OrphanDetailView(DetailView):
    model = Orphan
