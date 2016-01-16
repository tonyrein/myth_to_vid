from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView

from orphans.models import Orphan
# Create your views here.

class OrphanListView(ListView):
    model = Orphan
    
