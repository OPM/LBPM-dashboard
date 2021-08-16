import os
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pylab as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.http import HttpResponse

def create_input_database(filename, content):
   infile = open(filename,'w')
   infile.write(content)
   infile.close()

def write_input_database(filename, content):
   infile = open(filename,'a')
   infile.write(content)
   infile.close()

def read_input_database(filename):
   infile = open(filename,'r')
   content = infile.read()
   return content

def generate_upload_path(instance, filename):
   return os.path.join('simulation/%s/' % instance.id, filename)

def view_slice(request):
   response = HttpResponse(content_type = 'image/png')
   imageFile = request.FILES.get('image')
   #handle_uploaded_file(request.FILES[imageFile])                                                                         
   filename = imageFile.name
   #filename = "myfile.dat"                                                                                                
   Nx = int(request.POST.get('Nx'))
   Ny = int(request.POST.get('Ny'))
   Nz = int(request.POST.get('Nz'))
   [npx, npy, npz, nx, ny, nz] = domain_decomp(Nx, Ny, Nz, 4)
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
   plt.savefig(response)
   return response

def domain_decomp(Nx, Ny, Nz, nprocs):
    nprocx = 1
    nprocy = 1
    nprocz = nprocs
    nx = Nx
    ny = Ny
    nz = Nz / nprocs
    # try to get load balancing to mach this ratio
    shortest = min(nx,ny,nz)
    ratio_x = nx/shortest
    ratio_y = ny/shortest
    ratio_z = nz/shortest
    print(ratio_x, ratio_y, ratio_z)
    # iterate with these values
    best_value = max(ratio_x,ratio_y,ratio_z)
    for i in range (1, nprocs):
        for j in range (1, nprocs):
            for k in range (1, nprocs):
                if nprocs == (i*j*k):
                    print(i,j,k)
                    x = Nx/i
                    y = Ny/j
                    z = Nz/k
                    shortest = min(x,y,z)
                    ratio_x = x/shortest
                    ratio_y = y/shortest
                    ratio_z = z/shortest
                    ratio = max(ratio_x,ratio_y,ratio_z)
                    if (ratio < best_value):
                        best_value = ratio
                        nprocx = i
                        nprocy = j
                        nprocz = k
                        print(best_value,i,j,k)
    
    nx = Nx/nprocx
    ny = Ny/nprocy
    nz = Nz/nprocz
    #if nprocs%p == 0:
    
    return [nx, ny, nz, nprocx, nprocy, nprocz]
