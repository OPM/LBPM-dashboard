from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
    #path('index', views.index, name='index'),
    path('upload', views.dataset_image_upload, name='upload'),
    #path('my_projects',views.my_projects, name='my_projects'),
    url(r'^my/$', views.my_projects, name='my_projects'),
    url(r'^(?P<project_id>\d+?)/?$', views.view_project, name='view_project'),
    url(r'^(?P<project_id>\d+?)/datasets/$',
        views.project_add_dataset, name="project_add_dataset"),
    url(r'^new/$', views.create_project, name='create_project'),
    url(r'^(?P<project_id>\d+?)/edit/$', views.project_edit_metadata, name='edit_project'),
    url(r'^(?P<project_id>\d+?)/collaborators/$', views.add_collaborator, name="project_add_collaborator"),

    url(r'^(?P<project_id>\d+?)/collaborators/(?P<collaborator_id>\d+?)/remove/$',
        views.remove_collaborator, name="project_remove_collaborator"),

    url(r'^(?P<project_id>\d+?)/collaborators/(?P<collaborator_id>\d+?)/status/$',
        views.update_collab_status, name="update_collab_status"), 
    url(r'^(?P<project_id>\d+?)/origin_data/(?P<origin_data_id>\d+?)/$',
        views.origin_data_summary, name="origin_data_summary"),
   #path('simulation', views.simulation, name='simulation'),
    #path('input', views.simulation, name='input'),
]


#   url(r'^$', views.browse_projects, name='browse_projects'),


#    url(r'^(?P<project_id>\d+?)/origin_data/(?P<origin_data_id>\d+?)/edit/$',
#        views.origin_edit_metadata, name="origin_data_edit"),

#    url(r'^(?P<project_id>\d+?)/origin_data/(?P<origin_data_id>\d+?)/upload/$',
#        views.dataset_image_upload, name="origin_data_image_upload"),
