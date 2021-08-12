from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from django.urls import reverse
from django.http import HttpResponse

from .forms import ColorForm
from .models import ImageData
from .forms import ImageDataForm

import os
import numpy as np
import matplotlib.pylab as plt

def index(request):
   return get_color(request)

def preview_image(request, SimPath):
   imageFile = request.FILES.get('image')
   #handle_uploaded_file(request.FILES[imageFile])
   filename = imageFile.name
   #filename = "myfile.dat"
   Nx = int(request.POST.get('Nx'))
   Ny = int(request.POST.get('Ny'))
   Nz = int(request.POST.get('Nz'))
   voxel_length = float(request.POST.get('voxel_length'))
   # check the input data
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
   LBPM_input_file = "Domain {\n"
   LBPM_input_file += '   filename = "'+str(filename)+'"'+"\n"
   #LBPM_input_file += '   path = "'+str(SimPath)+'"'+"\n"
   LBPM_input_file += '   voxel_length = '+str(voxel_length)+"\n"
   LBPM_input_file += "   N = "+str(Nx)+", "+str(Ny)+", "+str(Nz)+"\n"
   #LBPM_input_file += "   n = "+Nx+", "+Ny+", "+Nz+"\n"
   #LBPM_input_file += "   nproc = 1, 1, 1 \n"
   return render(request, 'LBPM/preview.html', {'inputfile':LBPM_input_file})


def simulation(request):
   #imageFile = request.FILES.get('image')
   #handle_uploaded_file(request.FILES[imageFile])
   filename = request.POST.get('image')
   protocol = request.POST.get('protocol')
   #filename = "myfile.dat"
   Nx = request.POST.get('Nx')
   Ny = request.POST.get('Ny')
   Nz = request.POST.get('Nz')
   voxel_length = request.POST.get('voxel_length')
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
      nu_w = nu_n*kinematic_viscosity_ratio
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
   LBPM_input_file = "Domain {\n"
   LBPM_input_file += '   filename = "'+filename+'"'+"\n"
   LBPM_input_file += '   voxel_length = '+voxel_length+"\n"
   LBPM_input_file += "   N = "+Nx+", "+Ny+", "+Nz+"\n"
   LBPM_input_file += "   n = "+Nx+", "+Ny+", "+Nz+"\n"
   LBPM_input_file += "   nproc = 1, 1, 1 \n"
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
      LBPM_input_file += '   protocol = "shell aggregation"'+"\n"
   elif protocol ==  "Image sequence" :
      LBPM_input_file += '   protocol = "image sequence"'+"\n"
   LBPM_input_file += '   rhoA = '+str(rho_n)+"\n"
   LBPM_input_file += '   rhoB = '+str(rho_w)+"\n"
   LBPM_input_file += '   tauA = '+str(tau_n)+"\n"
   LBPM_input_file += '   tauB = '+str(tau_w)+"\n"
   LBPM_input_file += '   alpha = '+str(alpha)+"\n"
   LBPM_input_file += '   beta = '+str(beta)+"\n"
   LBPM_input_file += "   F = "+str(Fx)+", "+str(Fy)+", "+str(Fz)+"\n"
   if protocol == "Core flooding" :
      LBPM_input_file += "   flux = "+str(flux)+"\n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "Analysis {\n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "Visualization {\n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "FlowAdaptor {\n"
   LBPM_input_file += "}\n"
   print(LBPM_input_file)
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
            #form.save()
            #Nx = request.POST.get('Nx')
            #Ny = request.POST.get('Ny')
            #Nz = request.POST.get('Nz')
            #voxel_length = request.POST.get('voxel_length')
            # redirect to a new URL:            
            #return HttpResponseRedirect('preview')
            return preview_image(request,filepath)

    # if a GET (or any other method) we'll create a blank form
    else:
        print("Get image data")
        form = ImageDataForm()
  
    return render(request, 'LBPM/image.html', {'form': form})

   
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

 
