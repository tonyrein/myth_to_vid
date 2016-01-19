from django.conf.urls import url
from orphans.views import OrphanDeleteView, OrphanDetailView, OrphanListView, OrphanUpdateView

urlpatterns = [
    url(r'^$', OrphanListView.as_view(), name='OrphanListView'),
    url(r'^update/(?P<pk>\d+)/$', OrphanUpdateView.as_view(), name='OrphanUpdateView'),
    url(r'^delete/(?P<pk>\d+)/$', OrphanDeleteView.as_view(), name='OrphanDeleteView'),
    url(r'^(?P<pk>\d+)/$', OrphanDetailView.as_view(), name='OrphanDetailView'),
               
]