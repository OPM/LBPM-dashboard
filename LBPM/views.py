from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from django.urls import reverse
from django.http import HttpResponse
from django.forms import modelformset_factory

from .forms import ColorForm
from .models import ImageData
from .models import VoxelLabel
from .forms import ImageDataForm
from .lbpm import *

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt

def index(request):
   return get_color(request)

def preview_slice(request, SimPath):
   response = HttpResponseRedirect('LBPM/preview.html', content_type = 'image/png')
   imageFile = request.FILES.get('image')
   #handle_uploaded_file(request.FILES[imageFile])                                                                      
      
   filename = imageFile.name
   #filename = "myfile.dat"                                                                                              
      
   Nx = int(request.POST.get('Nx'))
   Ny = int(request.POST.get('Ny'))
   Nz = int(request.POST.get('Nz'))
   [npx, npy, npz, nx, ny, nz] = domain_decomp(Nx, Ny, Nz, 4)
   voxel_length = float(request.POST.get('voxel_length'))
   # check the input image                                    

   input_file = os.path.join(SimPath,str(imageFile))
   slice_file = os.path.join(SimPath,str(imageFile)+"slice.png")
   ID = np.fromfile(input_file,dtype = np.uint8)
   ID.shape = (Nz,Ny,Nx)
   slice_at_x = int(Nx/2)
   plt.figure(1)
   plt.title(str(imageFile))
   plt.pcolormesh(ID[:,:,slice_at_x],cmap='hot')
   plt.grid(True)
   plt.axis('equal')
   plt.savefig(response)
   return response

def get_image_labels(request):
    ImageLabelFormSet = modelformset_factory(VoxelLabel, fields=('voxel_class','value'))
    if request.method == 'POST':
        formset = ImageLabelFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            # do something.
    else:
        formset = ImageLabelFormSet()
    return render(request, 'LBPM/image_labels.html', {'formset': formset})

def preview_image(request, SimPath):
   imageFile = request.FILES.get('image')
   #handle_uploaded_file(request.FILES[imageFile])                             
   filename = imageFile.name
   #filename = "myfile.dat"
   Nx = int(request.POST.get('Nx'))
   Ny = int(request.POST.get('Ny'))
   Nz = int(request.POST.get('Nz'))
   [nx, ny, nz, npx, npy, npz] = domain_decomp(Nx, Ny, Nz, 4)
   voxel_length = float(request.POST.get('voxel_length'))
   # check the input data
   input_db = os.path.join(SimPath,"input.db")
   input_file = os.path.join(SimPath,str(imageFile))
   slice_file = os.path.join(SimPath,str(imageFile)+"slice.png")
   ID = np.fromfile(input_file,dtype = np.uint8)
   ID.shape = (Nz,Ny,Nx)
   slice_at_x = int(Nx/2)
   plt.figure(1)
   plt.title(str(imageFile))
   plt.pcolormesh(ID[:,:,slice_at_x],cmap='hot')
   plt.grid(True)
   plt.axis('equal')
   plt.savefig(slice_file)

   read_values = np.unique(ID)
   print(read_values)

   relative_path = os.path.relpath(slice_file,settings.BASE_DIR)

   LBPM_input_file = "Domain {\n"
   LBPM_input_file += '   Filename = "'+str(filename)+'"'+"\n"
   LBPM_input_file += '   voxel_length = '+str(voxel_length)+"\n"
   LBPM_input_file += "   N = "+str(Nx)+", "+str(Ny)+", "+str(Nz)+"\n"
   LBPM_input_file += "   n = "+str(nx)+", "+str(ny)+", "+str(nz)+"\n"
   LBPM_input_file += "   nproc = "+str(npx)+", "+str(npy)+", "+str(npz)+"\n"  
   LBPM_input_file += '   ReadType ="8bit"'+"\n"
   LBPM_input_file += "   ReadValues = "
   for value in read_values :
      LBPM_input_file +=   str(value) + ", "
   LBPM_input_file += "\n"
   LBPM_input_file += "   WriteValues = "
   for value in read_values :
      LBPM_input_file +=   str(value) + ", "
   LBPM_input_file += "\n"
   create_input_database(input_db,LBPM_input_file)
   return render(request, 'LBPM/preview.html', {'inputfile':input_db, 'slice':relative_path})


def simulation(request):
   input_db=request.POST.get('input',"input.db")
   print(input_db)
   #input_db = request.POST.get('inputfile')
   protocol = request.POST.get('protocol')
   #Nx = request.POST.get('Nx')
   #Ny = request.POST.get('Ny')
   #Nz = request.POST.get('Nz')
   #voxel_length = request.POST.get('voxel_length')
   capillary_number = float(request.POST.get('capillary_number'))
   viscosity_ratio = float(request.POST.get('viscosity_ratio'))
   density_ratio = float(request.POST.get('density_ratio'))
   interfacial_tension = float(request.POST.get('interfacial_tension'))
   ift_units = request.POST.get('ift_units')
   kinematic_viscosity_ratio = viscosity_ratio / density_ratio
   tau = 0.7
   nu = (tau-0.5)/3
   flux = 0.0
   BC = 0
   alpha = 0.01
   beta = 0.95
   if ift_units == "LBM" :
      alpha = interfacial_tension / 6.0
   else :
      alpha = 0.008
   if kinematic_viscosity_ratio > 1.0 :
      nu_w = nu
      tau_w = tau
      nu_n = nu_w*kinematic_viscosity_ratio
      tau_n = 3*nu_n + 0.5
   else :
      nu_n = nu
      tau_n = tau
      nu_w = nu_n/kinematic_viscosity_ratio
      tau_w = 3*nu_w + 0.5
   if nu_w > 1.5 :
      print("Warning: phase w kinematic viscosity too high!")
      nu_w = 1.5
   rho_w = 1.0
   rho_n = rho_w*density_ratio
   if protocol == "Steady-state relperm" :
      Fx = 0.0
      Fy = 0.0
      Fz = 1.0e-5
   elif protocol == "Centrifuge" :
      Fx = 0.0
      Fy = 0.0
      Fz = 1.0e-5
      BC = 3
   elif protocol == "Core flooding" :
      Fx = 0.0
      Fy = 0.0
      Fz = 0.0
      flux = capillary_number*interfacial_tension/(rho_w*nu_w)
      BC = 4
   elif protocol ==  "Image sequence" :
      Fx = 0.0
      Fy = 0.0
      Fz = 1.0e-5
   #LBPM_input_file = "Domain {\n"
   #LBPM_input_file += '   filename = "'+filename+'"'+"\n"
   #LBPM_input_file += '   voxel_length = '+voxel_length+"\n"
   #LBPM_input_file += "   N = "+Nx+", "+Ny+", "+Nz+"\n"
   #LBPM_input_file += "   n = "+Nx+", "+Ny+", "+Nz+"\n"
   #LBPM_input_file += "   nproc = 1, 1, 1 \n"
   LBPM_input_file = "   // keys below set by color model\n"
   LBPM_input_file += '   BC = '+str(BC)+"\n"
   if protocol == "Steady-state relperm" :
      LBPM_input_file += "   InletLayers = 0, 0, 5 \n"
      LBPM_input_file += "   OutletLayers = 0, 0, 5 \n"
   elif protocol == "Image sequence" :
      LBPM_input_file += "   InletLayers = 0, 0, 5 \n"
      LBPM_input_file += "   OutletLayers = 0, 0, 5 \n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "Color {\n"   
   #LBPM_input_file += '   protocol = "'+protocol+'"'+"\n"
   if protocol == "Steady-state relperm" :
      LBPM_input_file += '   protocol = "fractional flow"'+"\n"
   elif protocol ==  "Image sequence" :
      LBPM_input_file += '   protocol = "image sequence"'+"\n"
   elif protocol ==  "Centrifuge" :
      LBPM_input_file += '   protocol = "centrifuge"'+"\n"
   elif protocol ==  "Core flooding" :
      LBPM_input_file += '   protocol = "core flooding"'+"\n"
   LBPM_input_file += '   rhoA = '+str(rho_n)+"\n"
   LBPM_input_file += '   rhoB = '+str(rho_w)+"\n"
   LBPM_input_file += '   tauA = '+str(tau_n)+"\n"
   LBPM_input_file += '   tauB = '+str(tau_w)+"\n"
   LBPM_input_file += '   alpha = '+str(alpha)+"\n"
   LBPM_input_file += '   beta = '+str(beta)+"\n"
   LBPM_input_file += "   F = "+str(Fx)+", "+str(Fy)+", "+str(Fz)+"\n"
   # NEED TO RETHINK THE COMPONENT LABEL ASSIGNMENT
   LBPM_input_file += "   ComponentLabels = 0\n"
   LBPM_input_file += "   ComponentAffinity = 1.0\n"
   LBPM_input_file += '   WettingConvention = "SCAL"'+"\n"
   if protocol == "Core flooding" :
      LBPM_input_file += "   flux = "+str(flux)+"\n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "Analysis {\n"
   LBPM_input_file += '   analysis_interval = 1000'+"\n"
   LBPM_input_file += "   restart_interval = 10000000\n"
   LBPM_input_file += '   restart_file = "Restart"'+"\n"
   if protocol != "Steady-state relperm" :
      LBPM_input_file += '   subphase_analysis_interval = 5000'+"\n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "Visualization {\n"
   LBPM_input_file += '   write_silo = false'+"\n"
   if protocol == "Steady-state relperm" :
      LBPM_input_file += '   visualization_interval = 5000000'+"\n"
   else :
      LBPM_input_file += '   visualization_interval = 500000'+"\n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "FlowAdaptor {\n"
   if protocol == "Steady-state relperm" :
      LBPM_input_file += '   max_steady_timesteps = 200000'+"\n"
      LBPM_input_file += '   min_steady_timesteps = 100000'+"\n"
      LBPM_input_file += '   fractional_flow_increment = 0.1'+"\n"
      LBPM_input_file += '   mass_fraction_factor = 0.0002'+"\n"
      LBPM_input_file += '   endpoint_threshold = 0.1'+"\n"
   LBPM_input_file += "}\n"
   print(LBPM_input_file)
   write_input_database(input_db,LBPM_input_file)
   LBPM_input_file = read_input_database(input_db)
   #imageFile.save()
   #Nx = form(request.POST['Nx'])
   print("Capillary number = %s" % str(capillary_number))
   print("Viscosity ratio = %s" % str(viscosity_ratio))
   print("Density ratio = %s" % str(density_ratio))
   print("interfacial tension = %s" % str(interfacial_tension))
   return render(request, 'LBPM/simulation.html', {'inputfile':LBPM_input_file})

   #   return HttpResponse(LBPM_input_file)
   
def get_image(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ImageDataForm(request.POST, request.FILES)
        # check whether it's valid:
        print('process image request')
        #print(ImageDataForm())
        if form.is_valid():
            print("save image")
            newimg = ImageData(image = request.FILES['image'])
            newimg.save()
            #filename = newimg.image.name
            filepath = os.path.dirname(newimg.image.path)
            #form.save() # this only works with ModelForm
            #Nx = request.POST.get('Nx')
            #Ny = request.POST.get('Ny')
            #Nz = request.POST.get('Nz')
            #voxel_length = request.POST.get('voxel_length')
            # redirect to a new URL:            
            #return HttpResponseRedirect('preview')
            return preview_image(request,filepath)
            #return preview_slice(request,filepath) ValueError here

    # if a GET (or any other method) we'll create a blank form
    else:
        print("Get image data")
        form = ImageDataForm()
  
    return render(request, 'LBPM/image.html', {'form': form})

def get_input(request):
   return HttpResponseRedirect('LBPM/input.html')
   
def get_color(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ColorForm(request.POST, request.FILES)
        # check whether it's valid:
        print('process color request')
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:            
            return HttpResponseRedirect('LBPM/index.html')

    # if a GET (or any other method) we'll create a blank form
    else:
        print("Get color data")
        form = ColorForm()
  
    return render(request, 'LBPM/color.html', {'form': form})

def show_color(request):
   return render(request)
    
def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def get_color_with_domain(request):
   print("Get color data")
   input_filename=request.POST.get('domain',"got nothing")
   print(input_filename)
   #input_db = forms.FilePathField(path=input_filename)
   #form.fields['inputfile'].widget = forms.HiddenInput()
   #initial={'inputfile':input_filename}
   form = ColorForm()
   return render(request, 'LBPM/color.html', {'form': form, 'inputfile':input_filename})

def show_color(request):
   return render(request)
    
def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = ImageDataForm(request.POST, request.FILES)
        if form.is_valid():
            newimg = ImageData(image = request.FILES['file'])
            newimg.save()
            Nx = request.POST.get('Nx')
            Ny = request.POST.get('Ny')
            Nz = request.POST.get('Nz')
            voxel_length = request.POST.get('voxel_length')

            # Redirect to the document list after POST
            #return HttpResponseRedirect(reverse('LBPM.views.list'))
            return render(request, 'LBPM/list.html', {'form': form})

    else:
        form = ImageDataForm() # A empty, unbound form

    # Load documents for the list page
    all_images = ImageData.objects.all()

    # Render list page with the documents and the form
    return render(request, 'LBPM/list.html', {'form': form})
    
    #return render_to_response(
    #    'LBPM/list.html',
    #    {'images': all_images, 'form': form},
    #    context_instance=RequestContext(request)
    #)

 
