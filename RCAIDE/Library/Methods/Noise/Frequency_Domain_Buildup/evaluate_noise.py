# RCAIDE/Library/Methods/Noise/Frequency_Domain/evaluate_noise_surrogates.py
#  
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE imports  
import RCAIDE 
from RCAIDE.Framework.Core import  Data  
from RCAIDE.Library.Methods.Noise.Common.decibel_arithmetic                           import SPL_arithmetic
from RCAIDE.Library.Methods.Noise.Common.generate_microphone_locations                import generate_zero_elevation_microphone_locations, generate_noise_hemisphere_microphone_locations
from RCAIDE.Library.Methods.Noise.Common.compute_relative_noise_evaluation_locations  import compute_relative_noise_evaluation_locations  
from RCAIDE.Library.Methods.Noise.Frequency_Domain_Buildup.Rotor.compute_rotor_noise  import compute_rotor_noise 
from RCAIDE.Library.Methods.Utilities                            import Cubic_Spline_Blender 

# package imports
import numpy                                                     as np  

# ----------------------------------------------------------------------------------------------------------------------
#  Vortex_Lattice
# ----------------------------------------------------------------------------------------------------------------------
## @ingroup Library-Methods-Stability  
def evaluate_noise_surrogate(state,settings,geometry):
    """ 
    """
    
    conditions    = state.conditions
    aerodynamics  = state.analyses.aerodynamics 
    AoA           = conditions.aerodynamics.angles.alpha 
    Mach          = conditions.freestream.mach_number
    
    SPL_dBA_sur     = settings.surrogates.SPL_dBA  
    SPL_spectra_sur = settings.surrogates.SPL_spectra
    
    len_eta   = len(conditions.energy)
    eta_names = list(conditions.energy.keys())
    etas = np.zeros((len(Mach),len_eta))
    for eta_i in range(len_eta):
        etas[:,eta_i]  = conditions.energy[eta_names[eta_i]].throttle
 
    geometry      = aerodynamics.geometry   
    
    pts    = np.hstack((AoA,Mach,etas)) 
    
    SPL_dBA      = np.atleast_2d(SPL_dBA_sur(pts)).T  
    SPL_spectra  = np.atleast_2d(SPL_spectra_sur(pts)).T    
  
    conditions.noise.total_SPL_dBA              = SPL_dBA
    conditions.noise.total_SPL_1_3_spectrum_dBA = SPL_spectra
        

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
        for tag , item in  network.items():
            if (tag == 'busses') or (tag == 'fuel_lines'): 
                for distributor in item: 
                    for propulsor in distributor.propulsors:
                        for sub_tag , sub_item in  propulsor.items():
                            if (sub_tag == 'rotor') or (sub_tag == 'propeller'):  
                                compute_rotor_noise(distributor,propulsor,conditions,settings) 
                                total_SPL_dBA     = SPL_arithmetic(np.concatenate((total_SPL_dBA[:,None,:],conditions.noise[distributor.tag][propulsor.tag][sub_item.tag].SPL_dBA[:,None,:]),axis =1),sum_axis=1)
                                total_SPL_spectra = SPL_arithmetic(np.concatenate((total_SPL_spectra[:,None,:,:],conditions.noise[distributor.tag][propulsor.tag][sub_item.tag].SPL_1_3_spectrum[:,None,:,:]),axis =1),sum_axis=1) 
                         
    conditions.noise.total_SPL_dBA              = total_SPL_dBA
    conditions.noise.total_SPL_1_3_spectrum_dBA = total_SPL_spectra
        
 
    return
 