# RCAIDE/Library/Methods/Noise/Frequency_Domain/build_noise_surrogates.py
#  
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE imports
from RCAIDE.Framework.Core import  Data 

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
    surrogates =  noise.surrogates
    training   =  noise.training 
    surrogates.noise    =  build_surrogate(noise,training.noise)  
    return

def build_surrogate(noise, training):
    
    # unpack data
    
    return surrogates
 