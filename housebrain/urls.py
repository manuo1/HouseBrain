from django.urls import path

from housebrain import views

app_name = 'housebrain'

urlpatterns = [
    path('', views.homepage, name='homepage'),
]
