## @ingroup  Library-Methods-Aerodynamics-Vortex_Lattice_Method
# RCAIDE/Library/Methods/Aerodynamics/Vortex_Lattice_Method/train_VLM_surrogates.py
#  
# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------

# RCAIDE imports  
import RCAIDE 
from RCAIDE.Framework.Core import  Data , Units 
from RCAIDE.Framework.Mission.Common                                                  import  Conditions  
from RCAIDE.Framework.Mission.Segments.Segment                                        import Segment  
from RCAIDE.Framework.Mission.Common                                                  import Results  
from RCAIDE.Library.Methods.Noise.Common.generate_microphone_locations                import generate_noise_hemisphere_microphone_locations
from RCAIDE.Library.Methods.Noise.Common.compute_relative_noise_evaluation_locations  import compute_relative_noise_evaluation_locations  
from RCAIDE.Library.Methods.Noise.Frequency_Domain_Buildup.Rotor.compute_rotor_noise  import compute_rotor_noise 
from RCAIDE.Library.Methods.Propulsors.Converters.Rotor.compute_rotor_performance     import compute_rotor_performance

# package imports
import numpy                                                     as np 
import time 

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
         
def compute_noise(training,distributor,propulsor,rotor,settings):
    '''
    
    
    
    '''

    ti        = time.time()    
    bus                            = RCAIDE.Library.Components.Energy.Distributors.Electrical_Bus() 
    electric_rotor                 = RCAIDE.Library.Components.Propulsors.Electric_Rotor()  
    electric_rotor.rotor           = rotor  
    bus.propulsors.append(electric_rotor)
    
    Machs = training.AoA        
    AoAs  = training.Mach       
    RPMs  = training.RPM         
    Alts  = training.altitude
    
    dim_cf   = len(settings.center_frequencies )  
    len_Mach = len(Machs)
    len_AoA  = len(AoAs) 
    len_RPM  = len(RPMs) 
    len_Alt  = len(Alts)
    
    settings.noise_hemisphere =  True 
    settings.noise_hemisphere_microphone_resolution = 10
    num_mic = int(settings.noise_hemisphere_microphone_resolution ** 2)
    training_SPL_dBA     = np.zeros((len_AoA,len_Mach,len_RPM,len_Alt,num_mic))
    training_SPL_spectra = np.zeros((len_AoA,len_Mach,len_RPM,len_Alt,num_mic,dim_cf)) 
    
    for Mach_i in range(len_Mach): 
        for RPM_i in range(len_RPM):  
            for alt_i in range(len_Alt): 
                # define atmospheric properties                                           
                atmosphere          = RCAIDE.Framework.Analyses.Atmospheric.US_Standard_1976()
                atmo_data           = atmosphere.compute_values(Alts[alt_i],0.0) 
                p                   = atmo_data.pressure          
                T                   = atmo_data.temperature       
                rho                 = atmo_data.density          
                a                   = atmo_data.speed_of_sound    
                mu                  = atmo_data.dynamic_viscosity      
                true_course         = 0
                fligth_path_angle   = 0    
              
                # Set up conditions data Structure     
                segment                    = Segment()  
                conditions                 = Results() 
                conditions.energy[bus.tag] = Conditions()
                conditions.noise[bus.tag]  = Conditions()
                segment.state.conditions   = conditions 
                electric_rotor.append_operating_conditions(segment,bus)
                for tag, item in  electric_rotor.items(): 
                    if issubclass(type(item), RCAIDE.Library.Components.Component):
                        item.append_operating_conditions(segment,bus,electric_rotor)
                conditions.expand_rows(len_AoA)
                
                # Set specific flight conditions  
                conditions.freestream.density[:,0]                     = rho
                conditions.freestream.dynamic_viscosity[:,0]           = mu 
                conditions.freestream.speed_of_sound[:,0]              = a 
                conditions.freestream.temperature[:,0]                 = T
                conditions.freestream.pressure[:,0]                    = p
                conditions.freestream.mach_number[:,0]                 = Machs[Mach_i] 
                conditions.frames.inertial.velocity_vector[:,0]        = Machs[Mach_i] *a
                conditions.frames.planet.true_course                   = np.zeros((len_AoA,3,3)) 
                conditions.frames.planet.true_course[:,0,0]            = np.cos(true_course),
                conditions.frames.planet.true_course[:,0,1]            = - np.sin(true_course)
                conditions.frames.planet.true_course[:,1,0]            = np.sin(true_course)
                conditions.frames.planet.true_course[:,1,1]            = np.cos(true_course) 
                conditions.frames.planet.true_course[:,2,2]            = 1 
                conditions.frames.wind.transform_to_inertial           = np.zeros((len_AoA,3,3))   
                conditions.frames.wind.transform_to_inertial[:,0,0]    = np.cos(fligth_path_angle) 
                conditions.frames.wind.transform_to_inertial[:,0,2]    = np.sin(fligth_path_angle) 
                conditions.frames.wind.transform_to_inertial[:,1,1]    = 1 
                conditions.frames.wind.transform_to_inertial[:,2,0]    = -np.sin(fligth_path_angle) 
                conditions.frames.wind.transform_to_inertial[:,2,2]    = np.cos(fligth_path_angle)  
                conditions.frames.body.transform_to_inertial           = np.zeros((len_AoA,3,3))
                conditions.frames.body.transform_to_inertial[:,0,0]    = np.cos(AoAs)
                conditions.frames.body.transform_to_inertial[:,0,2]    = np.sin(AoAs)
                conditions.frames.body.transform_to_inertial[:,1,1]    = 1
                conditions.frames.body.transform_to_inertial[:,2,0]    = -np.sin(AoAs)
                conditions.frames.body.transform_to_inertial[:,2,2]    = np.cos(AoAs)   

                conditions.aerodynamics.angles.alpha[:,0]              = AoAs
                rotor_conditions                                       = segment.state.conditions.energy[bus.tag][electric_rotor.tag][rotor.tag]     
                rotor_conditions.omega[:,0]                            = RPMs[RPM_i] *Units.rpm 
                compute_rotor_performance(electric_rotor,segment.state,bus)    
                
                # generate noise valuation points
                settings.noise_hemisphere_radius = Alts[alt_i]
                generate_noise_hemisphere_microphone_locations(settings)      
                
                RML,EGML,AGML,num_gm_mic,mic_stencil = compute_relative_noise_evaluation_locations(settings,conditions)
                  
                # append microphone locations to conditions  
                conditions.noise.ground_microphone_stencil_locations   = mic_stencil        
                conditions.noise.evaluated_ground_microphone_locations = EGML       
                conditions.noise.absolute_ground_microphone_locations  = AGML
                conditions.noise.number_of_ground_microphones          = num_gm_mic 
                conditions.noise.relative_microphone_locations         = RML 
                conditions.noise.total_number_of_microphones           = num_gm_mic 

                compute_rotor_noise(bus,electric_rotor,rotor,conditions,settings) 
                training_SPL_dBA[:,Mach_i,RPM_i, alt_i]      = conditions.noise[bus.tag][electric_rotor.tag][rotor.tag].SPL_dBA 
                training_SPL_spectra[:,Mach_i, RPM_i,  alt_i] = conditions.noise[bus.tag][electric_rotor.tag][rotor.tag].SPL_1_3_spectrum 
    
                
    tf           = time.time()
    elapsed_time = round((tf-ti),2)
    print('Simulation Time: ' + str(elapsed_time) )
    training.data[rotor.tag]             = Conditions()
    training.data[rotor.tag].SPL_dBA     = training_SPL_dBA     
    training.data[rotor.tag].SPL_spectra = training_SPL_spectra 
                         
    return