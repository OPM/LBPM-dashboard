from django.db import models

class ColorModel(models.Model):
      image = models.FileField(upload_to='simulation/%Y/%m/%d')
      #image = models.FilePathField(path="/home/mcclurej/")
      protocol = models.CharField(max_length=256,default="Image sequence")
      Nx = models.IntegerField(default=3)
      Ny = models.IntegerField(default=3)
      Nz = models.IntegerField(default=3)
      capillary_number = models.FloatField(default=0.00001)
      viscosity_ratio = models.FloatField(default=1.0)
      density_ratio = models.FloatField(default=1.0)
      interfacial_tension = models.FloatField(default=0.01)

      #class Question(models.Model):
#    question_text = models.CharField(max_length=200)
#    pub_date = models.DateTimeField('date published')


#class Choice(models.Model):
#    question = models.ForeignKey(Question, on_delete=models.CASCADE)
#    choice_text = models.CharField(max_length=200)
#    votes = models.IntegerField(default=0)
