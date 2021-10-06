from django.urls import path

from housebrain import views

app_name = 'housebrain'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('heating_periods', views.heating_periods, name='heating_periods'),

]
