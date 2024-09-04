## @ingroup  Library-Methods-Aerodynamics-Vortex_Lattice_Method
# RCAIDE/Library/Methods/Aerodynamics/Vortex_Lattice_Method/train_VLM_surrogates.py
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
# package imports
import numpy                                                     as np 

# ----------------------------------------------------------------------------------------------------------------------
# Train Noise Surrogates 
# ----------------------------------------------------------------------------------------------------------------------
def train_noise_surrogates(noise):
    """    
    """ 
    geometry   = noise.geometry
    settings   = noise.settings
    AoAs       = noise.training.angles_of_attack 
    etas       = noise.training.throttle
    Machs      = noise.training.Mach 
       
    len_AoA    = len(AoAs)   
    len_Mach   = len(Machs) 
    len_eta    = len(etas)
    
    training =  Data() 
     
    len_unique_propulsors  = 0
    unique_propulsor_names = []
    for network in geometry.networks:
        for tag , item in  network.items():
            if (tag == 'busses') or (tag == 'fuel_lines'):
                identical = False 
                for distributor in item:
                    if identical:
                        unique_propulsor_names.append(distributor.tag)
                        len_unique_propulsors += 1
                identical = item.idendical_propulsors
    
    SPL_dBA               = np.zeros((len_AoA,len_Mach,len_eta,unique_propulsor_names)) 
    SPL_1_3_spectrum_dBA  = np.zeros((len_AoA,len_Mach,len_eta,unique_propulsor_names)) 
                                 
    for Mach_i in range(len_Mach):
        for p_i in  range(len_unique_propulsors):
            for eta_i in range(len_eta): 
                
                # reset conditions  
                conditions                                      = RCAIDE.Framework.Mission.Common.Results()
                conditions.expand_rows(len_AoA)
                
                # set mach number
                conditions.freestream.mach_number[0,:]          = Machs[Mach_i]
                
                # set angle of attack
                conditions.aerodynamics.angles.alpha[0,:]       = AoAs                 
            
                # set throttle
                conditions.energy[unique_propulsor_names[p_i]].throttle = etas[eta_i] 
                
                evaluate_noise(conditions,settings,geometry)
                
                SPL_dBA[:,Mach_i,p_i,eta_i]              =  conditions.noise.total_SPL_dBA
                SPL_1_3_spectrum_dBA[:,Mach_i,p_i,eta_i] =  conditions.noise.total_SPL_1_3_spectrum_dBA
        
    training.SPL_dBA              = SPL_dBA             
    training.SPL_1_3_spectrum_dBA = SPL_1_3_spectrum_dBA
    
    return training
         
 
        
# ----------------------------------------------------------------------
#  Evaluate Noise
# ----------------------------------------------------------------------
def evaluate_noise(conditions,settings,geometry):
    """   
    """
    """ 
    """          
    # unpack   
    dim_cf        = len(settings.center_frequencies) 
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