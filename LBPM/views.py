from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import ColorForm
from django.http import HttpResponse

def index(request):
   return get_color(request)

def simulation(request):
  # imageFile = request.FILES.get('image')
   filename = request.POST.get('image')
   protocol = request.POST.get('protocol')
   #filename = "myfile.dat"
   Nx = request.POST.get('Nx')
   Ny = request.POST.get('Ny')
   Nz = request.POST.get('Nz')
   capillary_number = request.POST.get('capillary_number')
   viscosity_ratio = request.POST.get('viscosity_ratio')
   density_ratio = request.POST.get('density_ratio')
   interfacial_tension = request.POST.get('interfacial_tension')
   LBPM_input_file = "Domain {\n"
   LBPM_input_file += '   filename = "'+filename+'"'+"\n"
   LBPM_input_file += "   N = "+Nx+", "+Ny+", "+Nz+"\n"
   LBPM_input_file += "   n = "+Nx+", "+Ny+", "+Nz+"\n"
   LBPM_input_file += "   nproc = 1, 1, 1 \n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "Color {\n"   
   LBPM_input_file += '   protocol = "'+protocol+'"'+"\n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "Analysis {\n"
   LBPM_input_file += "}\n"
   LBPM_input_file += "Visualization {\n"
   LBPM_input_file += "}\n"
   print(LBPM_input_file)
   #imageFile.save()
   #Nx = form(request.POST['Nx'])
   print("Capillary number = %s" % capillary_number)
   print("Viscosity ratio = %s" % viscosity_ratio)
   print("Density ratio = %s" % density_ratio)
   print("interfacial tension = %s" % interfacial_tension)
   return render(request, 'LBPM/simulation.html', {'inputfile':LBPM_input_file})

   #   return HttpResponse(LBPM_input_file)

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
    
