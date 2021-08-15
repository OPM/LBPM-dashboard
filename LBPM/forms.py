from django import forms
from django.utils.safestring import mark_safe

from .models import *

PROTOCOLS= [
    ('Steady-state relperm', 'Steady-state relperm'),
    ('Centrifuge', 'Centrifuge'),
    ('Core flooding', 'Core Flooding'),
    ('Image sequence', 'Image Sequence')
    ]

IFT_UNITS= [
    ('LBM', 'LBM'),
    ('Pa-s', 'Pa-s'),
    ('dynes/cm', 'dynes/cm'),
    ('mN/m', 'mN/m')
    ]

class VoxelLabelForm(forms.ModelForm):
    class Meta:
        model = VoxelLabel
        fields = ['voxel_class', 'value']


class ColorForm(forms.Form):
    #inputfile = forms.FilePathField()
    protocol = forms.CharField(label=mark_safe('Simulation protocol'), widget=forms.Select(choices=PROTOCOLS))
    #file = forms.FileField(
    #    label='Select image file',
    #    help_text=''
    #)
    #Nx = forms.IntegerField(label=mark_safe('<br /> <br /> Nx'),min_value=3)
    #Ny = forms.IntegerField(label=mark_safe('  Ny'),min_value=3)
    #Nz = forms.IntegerField(label=mark_safe('  Nz'),min_value=3)
    #voxel_length = forms.FloatField(label=mark_safe('<br /> <br /> Voxel length (micron)'))
    capillary_number = forms.FloatField(label=mark_safe('<br /> <br /> Capillary Number'),max_value=1.0,min_value=1.0e-6)
    viscosity_ratio = forms.FloatField(label=mark_safe('<br /> <br />Viscosity Ratio'),min_value=0.01,max_value=100.0)
    density_ratio = forms.FloatField(label=mark_safe('<br /> <br />Density Ratio'),min_value=0.01,max_value=100.0)
    interfacial_tension = forms.FloatField(label=mark_safe('<br /> <br /> Interfacial Tension'),max_value=0.06,min_value=0.0)
    ift_units = forms.CharField(label=mark_safe('units'), widget=forms.Select(choices=IFT_UNITS))
    
    def clean_color_data(self):
        data = self.cleaned_data['filename']
        
        # Check if a date is not in the past. 
        #if data < datetime.date.today():
        #    raise ValidationError(_('Invalid date - renewal in past'))

        # Check if a date is in the allowed range (+4 weeks from today).
        #if data > datetime.date.today() + datetime.timedelta(weeks=4):
   
        # Remember to always return the cleaned data.
        return data


#class ImageDataForm(forms.ModelForm):
#    class Meta:
#        model = ImageData
#        fields = ['image', 'Nx', 'Ny', 'Nz', 'voxel_length']

class ImageDataForm(forms.Form):
    image = forms.FileField(
        label='Select a file',
        help_text='max. 1 gigabytes'
    )
    Nx = forms.IntegerField(label=mark_safe('<br /> <br /> Nx'),min_value=3)
    Ny = forms.IntegerField(label=mark_safe('  Ny'),min_value=3)
    Nz = forms.IntegerField(label=mark_safe('  Nz'),min_value=3)
    voxel_length = forms.FloatField(label=mark_safe('<br /> <br /> Voxel length (micron)'))

