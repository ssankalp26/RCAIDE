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
    training   = noise.training
    
    for network in geometry.networks:
        for tag , item in  network.items():
            if (tag == 'busses') or (tag == 'fuel_lines'): 
                for distributor in item: 
                    for propulsor in distributor.propulsors:
                        for sub_tag , sub_item in  propulsor.items():
                            if (sub_tag == 'rotor') or (sub_tag == 'propeller'):
                                compute_noise(training,distributor,propulsor,sub_item,settings) 
    
    return  
         
def compute_noise(training,distributor,propulsor,sub_item,settings): 
    Machs = training.AoA        
    AoAs  = training.Mach       
    RPMs  = training.RPM        
    Betas = training.blade_pitch 
    
    
    len_Mach = len(Machs)
    len_AoA  = len(AoAs) 
    len_RPM  = len(RPMs)
    len_Beta = len(Betas) 
                                  
    for Mach_i in range(len_Mach): 
        for RPM_i in range(len_RPM): 
            for Beta_i in range(len_Beta):
                # reset conditions  
                conditions                                      = RCAIDE.Framework.Mission.Common.Results()
                conditions.expand_rows(len_AoA)
                
                # set mach number
                conditions.freestream.mach_number[0,:]          = Machs[Mach_i]
                
                # set angle of attack
                conditions.aerodynamics.angles.alpha[0,:]       = AoAs                 
            
                # set throttle
                conditions.energy[unique_propulsor_names[p_i]].throttle = etas[eta_i] 
                
                    
                dim_cf        = len(settings.center_frequencies) 
                ctrl_pts      = len(conditions.freestream.density)
                
                # generate noise valuation points
                if settings.noise_hemisphere == True:
                    generate_noise_hemisphere_microphone_locations(settings)     
                    
                elif type(settings.ground_microphone_locations) is not np.ndarray: 
                    generate_zero_elevation_microphone_locations(settings)     
                
                RML,EGML,AGML,num_gm_mic,mic_stencil = compute_relative_noise_evaluation_locations(settings,conditions)
                  
                # append microphone locations to conditions  
                conditions.noise.ground_microphone_stencil_locations   = mic_stencil        
                conditions.noise.evaluated_ground_microphone_locations = EGML       
                conditions.noise.absolute_ground_microphone_locations  = AGML
                conditions.noise.number_of_ground_microphones          = num_gm_mic 
                conditions.noise.relative_microphone_locations         = RML 
                conditions.noise.total_number_of_microphones           = num_gm_mic 
                 
                 
                training[rotor.tag].
                training[rotor.tag].
 
    return