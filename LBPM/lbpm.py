import numpy as np

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
