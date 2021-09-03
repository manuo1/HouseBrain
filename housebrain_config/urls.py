"""housebrain_config URL Configuration"""

from django.contrib import admin
from django.urls import include,path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('housebrain.urls')),
    path('auth/', include('authentication.urls')),
    path('sensors/', include('sensors.urls')),
    path('rooms/', include('rooms.urls')),
    path('heaters/', include('heaters.urls')),
    path('teleinformation/', include('teleinformation.urls')),
]
