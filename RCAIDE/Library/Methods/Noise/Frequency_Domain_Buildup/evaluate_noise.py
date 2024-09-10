# RCAIDE/Library/Methods/Noise/Frequency_Domain/evaluate_noise_surrogates.py
#  
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE imports  
from RCAIDE.Framework.Core import  Data ,  Units
from RCAIDE.Library.Methods.Noise.Common.decibel_arithmetic                           import SPL_arithmetic
from RCAIDE.Library.Methods.Noise.Common.generate_microphone_locations                import generate_zero_elevation_microphone_locations, generate_noise_hemisphere_microphone_locations
from RCAIDE.Library.Methods.Noise.Common.compute_relative_noise_evaluation_locations  import compute_relative_noise_evaluation_locations  
from RCAIDE.Library.Methods.Noise.Frequency_Domain_Buildup.Rotor.compute_rotor_noise  import compute_rotor_noise 
from RCAIDE.Library.Methods.Noise.Common.decibel_arithmetic                           import SPL_arithmetic  
from RCAIDE.Library.Methods.Noise.Common.compute_noise_source_coordinates             import compute_rotor_point_source_coordinates 

# package imports
import numpy as np  
import scipy as sp

# ----------------------------------------------------------------------------------------------------------------------
#  Vortex_Lattice
# ----------------------------------------------------------------------------------------------------------------------
## @ingroup Library-Methods-Stability  
def evaluate_noise_surrogate(state,settings,geometry):
    """ 
    """

    # unpack  
    conditions    = state.conditions  
    dim_cf        = len(settings.center_frequencies ) 
    ctrl_pts      = len(conditions.freestream.density) 
    
    # generate noise valuation points
    if settings.noise_hemisphere == True:
        generate_noise_hemisphere_microphone_locations(settings)     
        
    elif type(settings.ground_microphone_locations) is not np.ndarray: 
        generate_zero_elevation_microphone_locations(settings)     
    
    RML,EGML,AGML,num_gm_mic,mic_stencil = compute_relative_noise_evaluation_locations(settings,state.conditions)
      
    # append microphone locations to conditions  
    conditions.noise.ground_microphone_stencil_locations   = mic_stencil        
    conditions.noise.evaluated_ground_microphone_locations = EGML       
    conditions.noise.absolute_ground_microphone_locations  = AGML
    conditions.noise.number_of_ground_microphones          = num_gm_mic 
    conditions.noise.relative_microphone_locations         = RML 
    conditions.noise.total_number_of_microphones           = num_gm_mic 
    
    # create empty arrays for results      
    total_SPL_dBA          = np.ones((ctrl_pts,num_gm_mic))*1E-16 
    total_SPL_spectra      = np.ones((ctrl_pts,num_gm_mic,dim_cf))*1E-16  
     
    # iterate through sources and iteratively add rotor noise 
    for network in geometry.networks: 
        for bus in network.busses:
            for propulsor in  bus.propulsors: 
                for sub_tag , sub_item in  propulsor.items():
                    if (sub_tag == 'rotor') or (sub_tag == 'propeller'):
                        query_noise_surrogate(bus,propulsor,sub_item,state,settings) 
                        total_SPL_dBA     = SPL_arithmetic(np.concatenate((total_SPL_dBA[:,None,:],conditions.noise[bus.tag][propulsor.tag][sub_item.tag].SPL_dBA[:,None,:]),axis =1),sum_axis=1)
                        total_SPL_spectra = SPL_arithmetic(np.concatenate((total_SPL_spectra[:,None,:,:],conditions.noise[bus.tag][propulsor.tag][sub_item.tag].SPL_1_3_spectrum_dBA[:,None,:,:]),axis =1),sum_axis=1) 
                        
                
        for fuel_line in network.fuel_lines:
            for propulsor in  fuel_line.propulsors: 
                for sub_tag , sub_item in  propulsor.items():
                    if (sub_tag == 'rotor') or (sub_tag == 'propeller'): 
                        query_noise_surrogate(fuel_line,propulsor,sub_item,state,settings) 
                        total_SPL_dBA     = SPL_arithmetic(np.concatenate((total_SPL_dBA[:,None,:],conditions.noise[fuel_line.tag][propulsor.tag][sub_item.tag].SPL_dBA[:,None,:]),axis =1),sum_axis=1)
                        total_SPL_spectra = SPL_arithmetic(np.concatenate((total_SPL_spectra[:,None,:,:],conditions.noise[fuel_line.tag][propulsor.tag][sub_item.tag].SPL_1_3_spectrum_dBA[:,None,:,:]),axis =1),sum_axis=1) 
                                                
                         
    conditions.noise.total_SPL_dBA              = total_SPL_dBA
    conditions.noise.total_SPL_1_3_spectrum_dBA = total_SPL_spectra
    
    return 
    
def query_noise_surrogate(distributor,propulsor,rotor,state,settings): 
        
    # unpack
    conditions           = state.conditions 
    noise                = state.analyses.noise 
    microphone_locations = conditions.noise.relative_microphone_locations 

    # create data structures for computation 
    Results = Data()

    # compute position vector from point source at rotor hub to microphones 
    coordinates = compute_rotor_point_source_coordinates(distributor,propulsor,rotor,conditions,microphone_locations,settings)     

    # Summation of spectra from propellers into into one SPL and store results
    
    # blade incidence angle to wind 
    angle_of_attack       = conditions.aerodynamics.angles.alpha # INCORRECT 
    orientation           = np.array(rotor.orientation_euler_angles) * 1  # INCORRECT 
    body2thrust           = sp.spatial.transform.Rotation.from_rotvec(orientation).as_matrix() # INCORRECT 
    AoA                   = angle_of_attack + np.arccos(body2thrust[0,0])  # INCORRECT
    
    # mach 
    Mach                  = conditions.freestream.mach_number
    
    # RPM
    RPM                   = state.conditions.energy[distributor.tag][propulsor.tag][rotor.tag].omega / Units.rpm

    num_gm_mic =  conditions.noise.number_of_ground_microphones 
    ctrl_pts   = len(conditions.freestream.density)  
    dim_cf     = len(settings.center_frequencies ) 
    
    # create empty arrays for results      
    SPL_dBA                = np.ones((ctrl_pts,num_gm_mic))*1E-16 
    SPL_1_3_spectrum_dBA   = np.ones((ctrl_pts,num_gm_mic,dim_cf))*1E-16  
    
        
    for i in range(conditions.noise.number_of_ground_microphones):
        # Distance 
        distance              = np.atleast_2d(np.linalg.norm(coordinates.X_hub_r[:,i,0,0,:], axis=1)).T
        
        # Phi
        phi =  np.atleast_2d(coordinates.phi_hub_r[:,i,0,0]).T
        
        # Theta    
        theta = np.atleast_2d(coordinates.theta_r[:,i,0,0]).T
        
        # combien points 
        pts                             = np.hstack((AoA, Mach, RPM, distance,phi,theta))
        
        # query surrogate
        SPL_dBA[:,i]              = noise.surrogates[rotor.tag].SPL_dBA(pts) 
        SPL_1_3_spectrum_dBA[:,i] = noise.surrogates[rotor.tag].SPL_1_3_spectrum_dBA(pts) 
   
    
    Results.SPL_dBA              = SPL_dBA
    Results.SPL_1_3_spectrum_dBA = SPL_1_3_spectrum_dBA
    
    # A-weighted
    conditions.noise[distributor.tag][propulsor.tag][rotor.tag] = Results
    

    return

 
def evaluate_noise_no_surrogate(state,settings,geometry):
    """ 
    """          
    # unpack  
    conditions    = state.conditions  
    dim_cf        = len(settings.center_frequencies ) 
    ctrl_pts      = len(conditions.freestream.density) 
    
    # generate noise valuation points
    if settings.noise_hemisphere == True:
        generate_noise_hemisphere_microphone_locations(settings)     
        
    elif type(settings.ground_microphone_locations) is not np.ndarray: 
        generate_zero_elevation_microphone_locations(settings)     
    
    RML,EGML,AGML,num_gm_mic,mic_stencil = compute_relative_noise_evaluation_locations(settings,state)
      
    # append microphone locations to conditions  
    conditions.noise.ground_microphone_stencil_locations   = mic_stencil        
    conditions.noise.evaluated_ground_microphone_locations = EGML       
    conditions.noise.absolute_ground_microphone_locations  = AGML
    conditions.noise.number_of_ground_microphones          = num_gm_mic 
    conditions.noise.relative_microphone_locations         = RML 
    conditions.noise.total_number_of_microphones           = num_gm_mic 
    
    # create empty arrays for results      
    total_SPL_dBA          = np.ones((ctrl_pts,num_gm_mic))*1E-16 
    total_SPL_spectra      = np.ones((ctrl_pts,num_gm_mic,dim_cf))*1E-16  
     
    # iterate through sources and iteratively add rotor noise 
    for network in geometry.networks: 
        for bus in network.busses:
            for propulsor in  bus.propulsors: 
                for sub_tag , sub_item in  propulsor.items():
                    if (sub_tag == 'rotor') or (sub_tag == 'propeller'):
                        compute_rotor_noise(bus,propulsor,sub_item,conditions,settings) 
                        total_SPL_dBA     = SPL_arithmetic(np.concatenate((total_SPL_dBA[:,None,:],conditions.noise[bus.tag][propulsor.tag][sub_item.tag].SPL_dBA[:,None,:]),axis =1),sum_axis=1)
                        total_SPL_spectra = SPL_arithmetic(np.concatenate((total_SPL_spectra[:,None,:,:],conditions.noise[bus.tag][propulsor.tag][sub_item.tag].SPL_1_3_spectrum[:,None,:,:]),axis =1),sum_axis=1) 
                        
                
        for fuel_line in network.fuel_lines:
            for propulsor in  fuel_line.propulsors: 
                for sub_tag , sub_item in  propulsor.items():
                    if (sub_tag == 'rotor') or (sub_tag == 'propeller'): 
                        compute_rotor_noise(fuel_line,propulsor,sub_item,conditions,settings) 
                        total_SPL_dBA     = SPL_arithmetic(np.concatenate((total_SPL_dBA[:,None,:],conditions.noise[fuel_line.tag][propulsor.tag][sub_item.tag].SPL_dBA[:,None,:]),axis =1),sum_axis=1)
                        total_SPL_spectra = SPL_arithmetic(np.concatenate((total_SPL_spectra[:,None,:,:],conditions.noise[fuel_line.tag][propulsor.tag][sub_item.tag].SPL_1_3_spectrum[:,None,:,:]),axis =1),sum_axis=1) 
                                                
                         
    conditions.noise.total_SPL_dBA              = total_SPL_dBA
    conditions.noise.total_SPL_1_3_spectrum_dBA = total_SPL_spectra
    return
 