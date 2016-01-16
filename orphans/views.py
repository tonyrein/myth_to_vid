from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView

from django_tables2 import tables, SingleTableView

from orphans.models import Orphan
# Create your views here.

# class OrphanListView(ListView):
#     model = Orphan


# table to use when displaying OrphanList
class OrphanListTable(tables.Table):
    class Meta:
        model = Orphan

class OrphanListView(SingleTableView):
    model = Orphan
    table_class = OrphanListTable
    

