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
    surrogates          = noise.surrogates
    training            = noise.training 
    surrogates.noise    = build_surrogate(noise,training.noise)  
    return

def build_surrogate(noise, training):
    
    # unpack data
    surrogates     = Conditions()
    Mach_data      = training.AoA        
    AoA_data       = training.Mach       
    RPM_data       = training.RPM         
    altitude_data  = training.altitude
    
    for data_set in noise.training.data.items():
        rotor_tag
        surrogates[rotor_tag]             = Conditions()
        surrogates[rotor_tag].SPL_dBA     = RegularGridInterpolator((AoA_data , Mach_data, RPM_data, altitude_data),data_set  ,method = 'linear',   bounds_error=False, fill_value=None) 
        surrogates[rotor_tag].SPL_spectra = RegularGridInterpolator((AoA_data , Mach_data, RPM_data, altitude_data),data_set  ,method = 'linear',   bounds_error=False, fill_value=None) 
  
    return surrogates
 