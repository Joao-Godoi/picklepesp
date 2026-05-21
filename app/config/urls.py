from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('groups/', include('tournament.urls_groups')),
    path('playoffs/', include('tournament.urls_playoffs')),
    path('placements/', include('tournament.urls_placements')),
]