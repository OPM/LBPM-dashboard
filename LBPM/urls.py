from django.urls import path

from . import views


#urlpatterns = patterns('LBPM.views',
#    url(r'^list/$', 'list', name='list'),
#)

urlpatterns = [
    path('index', views.index, name='index'),
    path('preview', views.preview_image, name='preview'),
    path('input', views.get_input, name='input'),
    path('image_labels', views.get_image_labels, name='image_labels'),
    path('image', views.get_image, name='image'),
    path('color', views.get_color_with_domain, name='color'),
    path('simulation', views.simulation, name='simulation'),
    path('list', views.list, name='list'),
    #path('list/<int:year>/', views.year_archive),
    #path('input', views.simulation, name='input'),
]
