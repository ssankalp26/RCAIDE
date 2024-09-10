# RCAIDE/Library/Methods/Noise/Frequency_Domain/build_noise_surrogates.py
#  
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE imports 
from RCAIDE.Framework.Mission.Common  import  Conditions  

# package imports 
from scipy.interpolate   import RegularGridInterpolator
from scipy               import interpolate
import  numpy as  np

# ----------------------------------------------------------------------------------------------------------------------
#  Vortex_Lattice
# ----------------------------------------------------------------------------------------------------------------------
## @ingroup Library-Methods-Stability    
def build_noise_surrogates(noise):
    """Build a surrogate using sample evaluation results.
    
    Assumptions:
        None
        
    Source:
        None

    Args:
        aerodynamics       : VLM analysis          [unitless] 
        
    Returns: 
        None  
    """   
    
    # unpack data
    surrogates     = noise.surrogates 
    Mach_data      = noise.training.Mach       
    AoA_data       = noise.training.AoA       
    RPM_data       = noise.training.RPM         
    distance_data  = noise.training.distance
    phi_data       = noise.training.settings.ground_microphone_phi_values   
    theta_data     = noise.training.settings.ground_microphone_theta_values  
    
    for rotor_tag, data_set in noise.training.data.items():  
        noise.surrogates[rotor_tag]                      = Conditions()
        noise.surrogates[rotor_tag].SPL_dBA              = RegularGridInterpolator((AoA_data , Mach_data, RPM_data, distance_data,phi_data,theta_data),noise.training.data[rotor_tag].SPL_dBA  ,method = 'linear',   bounds_error=False, fill_value=None) 
        noise.surrogates[rotor_tag].SPL_1_3_spectrum_dBA = RegularGridInterpolator((AoA_data , Mach_data, RPM_data, distance_data,phi_data,theta_data),noise.training.data[rotor_tag].SPL_1_3_spectrum_dBA  ,method = 'linear',   bounds_error=False, fill_value=None) 
  
    return surrogates
 