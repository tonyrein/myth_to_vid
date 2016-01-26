from django.conf.urls import url
from orphans.views import OrphanDeleteView, OrphanDetailView, OrphanListView, OrphanUpdateView

urlpatterns = [
    url(r'^$', OrphanListView.as_view(), name='OrphanListView'),
    url(r'^(?P<page>\d+)/$', OrphanListView.as_view(), name='OrphanListViewWithPage'),
    url(r'^(?P<sort>\w+)/$', OrphanListView.as_view(), name='OrphanListViewWithSort'),
    url(r'^(?P<page>\d+)/(?P<sort>\w+)/$', OrphanListView.as_view(), name='OrphanListViewWithPageAndSort'),
    url(r'^update/(?P<pk>\d+)/$', OrphanUpdateView.as_view(), name='OrphanUpdateView'),
    url(r'^delete/(?P<pk>\d+)/$', OrphanDeleteView.as_view(), name='OrphanDeleteView'),
    url(r'^delete/(?P<pk>\d+)/(?P<listpage>\d+)/$', OrphanDeleteView.as_view(), name='OrphanDeleteViewWithListPage'),
    url(r'^delete/(?P<pk>\d+)/(?P<listsort>\w+)/$', OrphanDeleteView.as_view(), name='OrphanDeleteViewWithListSort'),
    url(r'^delete/(?P<pk>\d+)/(?P<listpage>\d+)/(?P<listsort>\w+)/$', OrphanDeleteView.as_view(), name='OrphanDeleteViewWithListPageAndSort'),
    url(r'^(?P<pk>\d+)/$', OrphanDetailView.as_view(), name='OrphanDetailView'),
               
]