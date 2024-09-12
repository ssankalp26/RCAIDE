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
    surrogates         = noise.surrogates 
    Mach_data          = noise.training.Mach       
    AoA_data           = noise.training.AoA       
    RPM_data           = noise.training.RPM /1000         
    distance_data      = noise.training.distance / 1000
    dir_phi_data       = noise.training.settings.ground_microphone_directivity_phi_angles  
    dir_theta_data     = noise.training.settings.ground_microphone_directivity_theta_angles   
    
    for rotor_tag, data_set in noise.training.data.items():  
        noise.surrogates[rotor_tag]                      = Conditions()
        noise.surrogates[rotor_tag].SPL_dBA              = RegularGridInterpolator((AoA_data , Mach_data, RPM_data, distance_data,dir_phi_data,dir_theta_data),noise.training.data[rotor_tag].SPL_dBA  ,method = 'linear',   bounds_error=False, fill_value=None) 
        noise.surrogates[rotor_tag].SPL_1_3_spectrum_dBA = RegularGridInterpolator((AoA_data , Mach_data, RPM_data, distance_data,dir_phi_data,dir_theta_data),noise.training.data[rotor_tag].SPL_1_3_spectrum_dBA  ,method = 'linear',   bounds_error=False, fill_value=None) 
    
        SPL_dBA_sur , SPL_1_3_spectrum_dBA_sur =  test_surrogate(noise,surrogates,rotor_tag)
        
    # WE NEED TO CHECK RESULTS 
    return surrogates
 
def test_surrogate(noise,surrogates,rotor_surrogate_tag):

    Machs      = noise.training.Mach       
    AoAs       = noise.training.AoA       
    RPMs       = noise.training.RPM /1000         
    R_s        = noise.training.distance / 1000
    phis       = noise.training.settings.ground_microphone_directivity_phi_angles  
    thetas     = noise.training.settings.ground_microphone_directivity_theta_angles
    dim_cf     = len(noise.training.settings.center_frequencies )  
    
    len_Mach  = len(Machs)
    len_AoA   = len(AoAs) 
    len_RPM   = len(RPMs) 
    len_phi   = len(phis) 
    len_theta = len(thetas) 
    len_R     = len(R_s)
    

    # create empty arrays for results      
    SPL_dBA_sur               = np.ones((len_AoA,len_Mach,len_RPM,len_R,len_phi,len_theta)) 
    SPL_1_3_spectrum_dBA_sur  = np.ones((len_AoA,len_Mach,len_RPM,len_R,len_phi,len_theta,dim_cf)) 

    for AoA_i in range(len_AoA):         
        for Mach_i in range(len_Mach): 
            for RPM_i in range(len_RPM):  
                for r_i in range(len_R):
                    for phi_i in range(len_phi):
                        for theta_i in range(len_theta): 
                            AoA       = AoAs[AoA_i]
                            Mach      = Machs[Mach_i]
                            distance  = R_s[r_i]
                            RPM       = RPMs[RPM_i]  
                            phi       = phis[phi_i] 
                            theta     = thetas[theta_i]
                            
                            # combien points 
                            pts   = np.hstack((AoA, Mach, RPM, distance,phi,theta))
                            
                            # query surrogate
                            SPL_dBA_sur[AoA_i,Mach_i, RPM_i, r_i,phi_i]               = surrogates[rotor_surrogate_tag].SPL_dBA(pts) 
                            SPL_1_3_spectrum_dBA_sur[AoA_i,Mach_i, RPM_i, r_i,phi_i]  = surrogates[rotor_surrogate_tag].SPL_1_3_spectrum_dBA(pts)
    return SPL_dBA_sur ,  SPL_1_3_spectrum_dBA_sur
                        
