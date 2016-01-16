from django.conf.urls import url
from orphans.views import OrphanListView

urlpatterns = [
    url(r'^$', OrphanListView.as_view(), name='OrphanListView'),
               
]