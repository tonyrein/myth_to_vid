from django.conf.urls import url
from orphans.views import OrphanListView, OrphanUpdateView

urlpatterns = [
    url(r'^$', OrphanListView.as_view(), name='OrphanListView'),
    url(r'^(?P<pk>\d+)/$', OrphanUpdateView.as_view(), name='OrphanUpdateView'),
               
]