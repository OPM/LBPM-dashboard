from django import template
from django.urls import reverse
from django.conf import settings
import os

register = template.Library()

@register.simple_tag
def active_nav(request, url_patterns, include_children=False, **kwargs):
    for index, url_pattern in enumerate(url_patterns.split()):
        url = reverse(url_pattern, kwargs=kwargs)
        if include_children:
            if request.path.startswith(url):
                return 'active'
        else:
            if request.path == url:
                return 'active'
    return ''


@register.simple_tag
def upload_thumbnail(data_file):
    if data_file.file and not data_file.isNonImageFile:
        thumbnail_path = '%s.thumb.jpg' % data_file.file.path
        if os.path.isfile(thumbnail_path):
            thumbnail_url = '%s.thumb.jpg' % data_file.file.url
            return thumbnail_url

        if data_file.isNormalImageFile:
            # if normal image and file is web-viewable
            parts = os.path.splitext(data_file.file.path)
            if len(parts) > 1 and parts[1] in ['.jpg', '.jpeg', '.png', '.gif']:
                return data_file.file.url

    return '%s%s' % (settings.STATIC_URL, 'upload/images/default.png')


@register.simple_tag
def file_thumbnail(data_file):
    filename, file_extension = os.path.splitext(data_file.file.name)
    if file_extension == '.pdf':
        css_class = "fa fa-file-pdf-o fa-5x"
    elif file_extension == '.doc':
        css_class = "fa fa-file-word-o fa-5x"
    elif file_extension == ".txt":
        css_class = "fa fa-file-text fa-5x"
    elif file_extension == ".zip":
        css_class = "fa fa-file-archive-o fa-5x"
    elif file_extension == ".ppt":
        css_class = " fa fa-file-powerpoint-o fa-5x"
    else:
        css_class = "fa fa-file-text fa-5x"
    return css_class
