from django.urls import path
from django.urls import include, re_path
#from django.conf.urls import include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #path('index', views.index, name='index'),
    path('upload', views.dataset_image_upload, name='upload'),
    #path('my_projects',views.my_projects, name='my_projects'),
    re_path(r'^my/$', views.my_projects, name='my_projects'),

    re_path(r'^(?P<project_id>\d+?)/?$', views.view_project, name='view_project'),

    re_path(r'^(?P<project_id>\d+?)/datasets/$',
        views.project_add_dataset, name="project_add_dataset"),

    re_path(r'^(?P<project_id>\d+?)/origin_data/(?P<origin_data_id>\d+?)/edit/$',
        views.origin_edit_metadata, name="origin_data_edit"),

    re_path(r'^new/$', views.create_project, name='create_project'),

    re_path(r'^(?P<project_id>\d+?)/sample/new/$',
        views.add_sample, name="add_sample"),

    re_path(r'^(?P<project_id>\d+?)/sample/(?P<sample_id>\d+?)/$',
        views.view_sample, name="view_sample"),

    re_path(r'^(?P<project_id>\d+?)/images/(?P<image_id>\d+)/edit/$',
        views.edit_dataset_image, name='edit_dataset_image'),

    re_path(r'^(?P<project_id>\d+?)/sample/(?P<sample_id>\d+?)/edit/$',
        views.edit_sample, name="edit_sample"),

    re_path(r'^(?P<project_id>\d+?)/edit/$', views.project_edit_metadata, name='edit_project'),
    re_path(r'^(?P<project_id>\d+?)/collaborators/$', views.add_collaborator, name="project_add_collaborator"),

    re_path(r'^(?P<project_id>\d+?)/collaborators/(?P<collaborator_id>\d+?)/remove/$',
        views.remove_collaborator, name="project_remove_collaborator"),

    re_path(r'^(?P<project_id>\d+?)/collaborators/(?P<collaborator_id>\d+?)/status/$',
        views.update_collab_status, name="update_collab_status"), 

    re_path(r'^(?P<project_id>\d+?)/origin_data/(?P<origin_data_id>\d+?)/$',
        views.origin_data_summary, name="origin_data_summary"),

    re_path(r'^(?P<project_id>\d+?)/origin_data/(?P<origin_data_id>\d+?)/upload/$',
        views.dataset_image_upload, name="origin_data_image_upload"),
    re_path(r'^(?P<project_id>\d+?)/origin_data/(?P<origin_data_id>\d+?)/uploadNI/$',
        views.dataset_nonimage_upload, name="origin_data_nonimage_upload"),

   #path('simulation', views.simulation, name='simulation'),
    #path('input', views.simulation, name='input'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


#   re_path(r'^$', views.browse_projects, name='browse_projects'),


#    re_path(r'^(?P<project_id>\d+?)/origin_data/(?P<origin_data_id>\d+?)/edit/$',
#        views.origin_edit_metadata, name="origin_data_edit"),

