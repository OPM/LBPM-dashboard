from django import forms
from django.contrib.admin import widgets
from django.contrib.auth import get_user_model
from django.forms import ModelForm

from upload.models import project as Project, origin_data, analysis_data, sample, AdvancedImageFile, DataFile


#Publication,  \
#    NormalImageFile, AdvancedImageFile, ProjectPublicationRequest, DataFile, NonImageFile

import logging

logger = logging.getLogger('console')

class AddProjectForm(ModelForm):
    user_agreement_label = 'LBPM assumes no liability for any use of this software'

    user_agreement = forms.BooleanField(initial=False,
                                        required=True,
                                        label=user_agreement_label,)

    def __init__(self, *args, **kwargs):
        super(AddProjectForm, self).__init__(*args, **kwargs)
        self.fields['user_agreement'].required = True

    class Meta:
        model = Project
#        fields = ('name', 'description', 'cover_pic', 'user_agreement')
        fields = ('name',)
        labels = {
            'name': 'Name',
#            'description': 'Description',
#            'cover_pic': 'Project cover image',
        }

        help_texts = {
            'name': 'Choose a name to identify your simulation project',
#            'cover_pic': 'This image will be displayed in project thumbnails and search results',
#            'description': 'The description is used for search and retrieval of your dataset.',
        }



class DataFileUploadForm(ModelForm):
    """
    Form to upload non image data. Excludes the file object since this is directly
    handled in the views
    """
    source = forms.CharField()
    name = forms.CharField()
    size = forms.IntegerField()
    url = forms.URLField(required=False)
    basic = forms.BooleanField(required=False)

    class Meta:
        model = DataFile
        exclude = ['file', 'uploader']

    def clean(self):
        cleaned_data = super(DataFileUploadForm, self).clean()
        logger.debug(cleaned_data)

        source = cleaned_data.get('source')
        url = cleaned_data.get('url')
        if source != 'Local file' and not url:
            raise forms.ValidationError("A URL is required for %s uploads" % source)

        basic = cleaned_data.get('basic')
        return cleaned_data

class OriginDataForm(ModelForm):
    voxel_other = forms.CharField(required=False, label='Other')

    def __init__(self, project, *args, **kwargs):
        super(OriginDataForm, self).__init__(*args, **kwargs)
        self.fields['is_segmented'].empty_label = None
        self.fields['sample'].queryset = sample.objects.filter(project_id=project.id)

    class Meta:
        model = origin_data
        exclude = ['project', 'uploader', 'doi',]
#        fields = [
#            'name',
#            'voxel_x', 'voxel_y', 'voxel_z',
#            'voxel_units', 'voxel_other',
#            ]
#        widgets = {
 #           'is_segmented': forms.RadioSelect(),
 #           'provenance': forms.Textarea(attrs={'rows':3}),
#            }
        fields = [
            'name', 'provenance', 'external_url',
            'is_segmented', 'voxel_x', 'voxel_y', 'voxel_z',
            'voxel_units', 'voxel_other', 'sample',
            ]
        widgets = {
            'is_segmented': forms.RadioSelect(),
            'provenance': forms.Textarea(attrs={'rows':3}),
            }

        help_texts = {
            'provenance': 'Describe the origin dataset'
        }

class AnalysisDataForm(ModelForm):
    analysis_other = forms.CharField(required=False, label='Other')

    def __init__(self, project, *args, **kwargs):
        super(AnalysisDataForm, self).__init__(*args, **kwargs)
        self.fields['sample'].queryset = sample.objects.filter(project_id=project.id)
        self.fields['base_origin_data'].queryset = origin_data.objects.filter(project_id=project.id)

    class Meta:
        model = analysis_data
        exclude = ['project', 'uploader', 'doi',]
        fields = [
            'name', 'type', 'analysis_other', 'description', 'external_url',
            'sample', 'base_origin_data',
            ]
        widgets = {
            'description': forms.Textarea(attrs={'rows':3}),
            }
        help_texts = {
        }


#class NonImageUploadForm(DataFileUploadForm):
#    class Meta:
#        model = NonImageFile
#        exclude = ['file', 'uploader']


#class NormalImageUploadForm(DataFileUploadForm):
#    class Meta:
#        model = NormalImageFile
#        exclude = ['file', 'uploader']


class AdvancedImageUploadForm(DataFileUploadForm):
    class Meta:
        model = AdvancedImageFile
        fields = [
                'image_type',
                'width',
                'height',
                'numberOfImages',
                'offsetToFirstImage',
                'gapBetweenImages',
                'byteOrder',
            ]

    def clean(self):
        cleaned_data = super(AdvancedImageUploadForm, self).clean()
        logger.debug(cleaned_data)

        source = cleaned_data.get('source')
        url = cleaned_data.get('url')
        if source != 'Local file' and not url:
            raise forms.ValidationError("A URL is required for %s uploads" % source)

        basic = cleaned_data.get('basic')
        if not basic:
            image_type = cleaned_data.get('image_type')
            width = cleaned_data.get('width')
            height = cleaned_data.get('height')
            numberOfImages = cleaned_data.get('numberOfImages')
            offsetToFirstImage = cleaned_data.get('offsetToFirstImage')
            gapBetweenImages = cleaned_data.get('gapBetweenImages')
            byteOrder = cleaned_data.get('byteOrder')

            if not image_type:
                raise forms.ValidationError('Additional image image_type is required')

            if not width:
                raise forms.ValidationError('Additional image width is required')

            if not height:
                raise forms.ValidationError('Additional image height is required')

            if not numberOfImages:
                raise forms.ValidationError('Additional image numberofImages is required')

            if not offsetToFirstImage:
                cleaned_data['offsetToFirstImage'] = 0

            if not gapBetweenImages:
                cleaned_data['gapBetweenImages'] = 0

            if not byteOrder:
                raise forms.ValidationError('Additional image byteOrder is required')

        return cleaned_data


class AdvancedImageEditForm(ModelForm):
    class Meta:
        model = AdvancedImageFile
        fields = [
                'image_type',
                'width',
                'height',
                'numberOfImages',
                'offsetToFirstImage',
                'gapBetweenImages',
                'byteOrder',
                'use_binary_correction',
            ]

class SampleDataForm(ModelForm):
    class Meta:
        model = sample
        exclude = ['project', 'uploader']


class DataFileUploadForm(ModelForm):
    """
    Form to upload non image data. Excludes the file object since this is directly
    handled in the views
    """
    source = forms.CharField()
    name = forms.CharField()
    size = forms.IntegerField()
    url = forms.URLField(required=False)
    basic = forms.BooleanField(required=False)

    class Meta:
        model = DataFile
        exclude = ['file', 'uploader']

    def clean(self):
        cleaned_data = super(DataFileUploadForm, self).clean()
        logger.debug(cleaned_data)

        source = cleaned_data.get('source')
        url = cleaned_data.get('url')
        if source != 'Local file' and not url:
            raise forms.ValidationError("A URL is required for %s uploads" % source)

        basic = cleaned_data.get('basic')
        return cleaned_data


