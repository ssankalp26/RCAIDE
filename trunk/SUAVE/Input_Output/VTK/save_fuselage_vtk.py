## @ingroup Input_Output-VTK
# save_fuselage_vtk.py
# 
# Created:    Jun 2021, R. Erhard
# Modified: 
#  

from SUAVE.Plots.Geometry_Plots.plot_vehicle import generate_fuselage_points
import numpy as np

def save_fuselage_vtk(vehicle, filename, Results):
    """
    Saves a SUAVE fuselage object as a VTK in legacy format.

    Inputs:
       vehicle        Data structure of SUAVE vehicle                [Unitless] 
       filename       Name of vtk file to save                       [String]  
       Results        Data structure of wing and propeller results   [Unitless]
       
    Outputs:                                   
       N/A

    Properties Used:
       N/A 
    
    Assumptions:
       N/A
    
    Source:  
       None
    
    """    
    
    fus_pts = generate_fuselage_points(vehicle.fuselages.fuselage)
    num_fus_segs = np.shape(fus_pts)[0]
    if num_fus_segs == 0:
        print("No fuselage segments found!")
    else:
        write_fuselage_vtk(fus_pts,filename)

    return


def write_fuselage_vtk(fus_pts,filename):
    # Create file
    with open(filename, 'w') as f:
    
        #---------------------
        # Write header
        #---------------------
        header = ["# vtk DataFile Version 4.0"  ,     # File version and identifier
                  "\nSUAVE Model of Fuselage"   ,     # Title
                  "\nASCII"                     ,     # Data type
                  "\nDATASET UNSTRUCTURED_GRID" ]     # Dataset structure / topology
                  
        f.writelines(header) 
        
        #---------------------    
        # Write Points:
        #---------------------   
        fuse_size = np.shape(fus_pts)
        n_r       = fuse_size[0]
        n_a       = fuse_size[1]
        n_indices = (n_r)*(n_a)    # total number of cell vertices
        points_header = "\n\nPOINTS "+str(n_indices) +" float"
        f.write(points_header)
        
        for r in range(n_r):
            for a in range(n_a):
                
                xp = round(fus_pts[r,a,0],4)
                yp = round(fus_pts[r,a,1],4)
                zp = round(fus_pts[r,a,2],4)
            
                new_point = "\n"+str(xp)+" "+str(yp)+" "+str(zp)
                f.write(new_point)
    
        #---------------------    
        # Write Cells:
        #---------------------
        n            = n_a*(n_r-1) # total number of cells
        v_per_cell   = 4 # quad cells
        size         = n*(1+v_per_cell) # total number of integer values required to represent the list
        cell_header  = "\n\nCELLS "+str(n)+" "+str(size)
        f.write(cell_header)
        
        rlap=0
        for i in range(n): # loop over all nodes in blade
            if i==(n_a-1+n_a*rlap):
                # last airfoil face connects back to first node
                b    = i-(n_a-1)
                c    = i+1
                rlap = rlap+1
            else:
                b = i+1
                c = i+n_a+1
                
            a        = i
            d        = i+n_a
            new_cell = "\n4 "+str(a)+" "+str(b)+" "+str(c)+" "+str(d)
            
            f.write(new_cell)
    
        #---------------------        
        # Write Cell Types:
        #---------------------
        cell_type_header  = "\n\nCELL_TYPES "+str(n)
        f.write(cell_type_header)        
        for i in range(n):
            f.write("\n9")
    
        #--------------------------        
        # Write Scalar Cell Data:
        #--------------------------
        cell_data_header  = "\n\nCELL_DATA "+str(n)
        f.write(cell_data_header)    
        
        # First scalar value
        f.write("\nSCALARS i float 1")
        f.write("\nLOOKUP_TABLE default")  
        for i in range(n):
            new_idx = str(i)
            f.write("\n"+new_idx)
            
            
    f.close()
    return