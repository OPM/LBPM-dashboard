from django.db import models
import uuid
import os

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('/simulations', filename)

class ColorModel(models.Model):
      #image = models.FileField(upload_to='simulations/%Y/%m/%d')
      #image = models.FilePathField(path="/home/mcclurej/")
      protocol = models.CharField(max_length=256,default="Image sequence")
      #Nx = models.IntegerField(default=3)
      #Ny = models.IntegerField(default=3)
      #Nz = models.IntegerField(default=3)
      capillary_number = models.FloatField(default=0.00001)
      viscosity_ratio = models.FloatField(default=1.0)
      density_ratio = models.FloatField(default=1.0)
      interfacial_tension = models.FloatField(default=0.01)

class VoxelLabel(models.Model):
    SOLID = 'S'
    WATER = 'W'
    OIL = 'N'
    GAS = 'G'
    MICROPOROS = 'M'
    LABEL_CLASS = [
        (SOLID, 'Solid'),
        (WATER, 'Water'),
        (OIL, 'Oil'),
        (GAS, 'Gas'),
        (MICROPOROS, 'Micro-porosity'),
    ]
    voxel_class = models.CharField(
        max_length = 1,
        choices = LABEL_CLASS,
        default = WATER,
    )
    value = models.SmallIntegerField(
        default = 1
    )
    affinity = models.FloatField(
        default = 0.9
    )
    

class ImageData(models.Model):
    #path = get_file_path
    image = models.FileField(upload_to='simulations/%Y/%m/%d')
    Nx = models.IntegerField(default=3)
    Ny = models.IntegerField(default=3)
    Nz = models.IntegerField(default=3)
    voxel_length = models.IntegerField(default=1)
#    def filename(self):
#        return os.path.basename(self.image.name)
#    def filepath(self):
#        return os.path.basename(self.image.path)


#class Question(models.Model):
#    question_text = models.CharField(max_length=200)
#    pub_date = models.DateTimeField('date published')


#class Choice(models.Model):
#    question = models.ForeignKey(Question, on_delete=models.CASCADE)
#    choice_text = models.CharField(max_length=200)
#    votes = models.IntegerField(default=0)
