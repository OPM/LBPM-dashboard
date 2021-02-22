from django.urls import path

from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('color', views.get_color, name='color'),
    path('simulation', views.simulation, name='simulation'),
    #path('input', views.simulation, name='input'),
]
