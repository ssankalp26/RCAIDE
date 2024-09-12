## @ingroup Analyses-Noise
# RCAIDE/Framework/Analyses/Noise/Frequency_Domain_Buildup.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------  
# noise imports    
from RCAIDE.Framework.Core                                 import Units,  Data 
from .Noise                                                import Noise 
from RCAIDE.Framework.Analyses                             import Process 
from RCAIDE.Framework.Mission.Common                       import Conditions 
from RCAIDE.Library.Methods.Noise.Frequency_Domain_Buildup import *   

# package imports
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------
#  Frequency_Domain_Buildup
# ----------------------------------------------------------------------------------------------------------------------
## @ingroup Analyses-Noise
class Frequency_Domain_Buildup(Noise):
    """This is an acoustic analysis based on a collection of frequency domain methods 

     Assumptions: 
 
     Source:
     N/A
 
     Inputs:
     None
 
     Outputs:
     None
 
     Properties Used:
     N/A 
    """    
    
    def __defaults__(self):
        
        """ This sets the default values for the analysis.
        
            Assumptions:
            Ground microphone angles start in front of the aircraft (0 deg) and sweep in a lateral direction 
            to the starboard wing and around to the tail (180 deg)
            
            Source:
            N/A
            
            Inputs:
            None
            
            Output:
            None
            
            Properties Used:
            N/A
        """
        
        # Initialize quantities
        settings                                                               = self.settings
        settings.harmonics                                                     = np.arange(1,30) 
        settings.flyover                                                       = False    
        settings.approach                                                      = False
        settings.sideline                                                      = False
        settings.sideline_x_position                                           = 0 
        settings.print_noise_output                                            = False  
        settings.mean_sea_level_altitude                                       = True 
        settings.aircraft_destination_location                                 = np.array([0,0,0])
        settings.aircraft_departure_location                                   = np.array([0,0,0])
                               
        settings.topography_file                                               = None
        settings.ground_microphone_locations                                   = None   
        settings.ground_microphone_coordinates                                 = None
        settings.ground_microphone_x_resolution                                = 5  #100
        settings.ground_microphone_y_resolution                                = 5  #100
        settings.ground_microphone_x_stencil                                   = 2
        settings.ground_microphone_y_stencil                                   = 2
        settings.ground_microphone_min_x                                       = 1E-6
        settings.ground_microphone_max_x                                       = 1000 * Units.feet 
        settings.ground_microphone_min_y                                       = -450 * Units.feet 
        settings.ground_microphone_max_y                                       =  450 * Units.feet 
                               
        settings.noise_hemisphere                                              = False 
        settings.use_surrogate                                                 = True       
        settings.noise_hemisphere_radius                                       = 20 
        settings.noise_hemisphere_microphone_resolution                        = 20
        settings.noise_hemisphere_directivity_phi_angle_bounds                 = np.array([0,np.pi])
        settings.noise_hemisphere_directivity_theta_angle_bounds               = np.array([0,2*np.pi])
                  
                         
        # settings for acoustic frequency resolution         
        settings.center_frequencies                                            = np.array([16,20,25,31.5,40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, \
                                                                                           500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150,
                                                                                           4000, 5000, 6300, 8000, 10000])        
        settings.lower_frequencies                                             = np.array([14,18,22.4,28,35.5,45,56,71,90,112,140,180,224,280,355,450,560,710,\
                                                                                           900,1120,1400,1800,2240,2800,3550,4500,5600,7100,9000 ])
        settings.upper_frequencies                                             = np.array([18,22.4,28,35.5,45,56,71,90,112,140,180,224,280,355,450,560,710,900,1120,\
                                                                                 1400,1800,2240,2800,3550,4500,5600,7100,9000,11200 ])

        self.training                                                          = Conditions()
        self.training.settings                                                 = Data()
        self.training.settings.noise_hemisphere                                = True 
        self.training.settings.use_surrogate                                   = True       
        self.training.settings.noise_hemisphere_radius                         = 10 
        self.training.settings.noise_hemisphere_microphone_resolution          = 10
        self.training.settings.noise_hemisphere_directivity_phi_angle_bounds   = np.array([0,2*np.pi])
        self.training.settings.noise_hemisphere_directivity_theta_angle_bounds = np.array([0,2*np.pi]) 
        self.training.settings.harmonics                                       = np.arange(1,30)  
        self.training.settings.center_frequencies                              = np.array([16,20,25,31.5,40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, \
                                                                                           500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150,
                                                                                           4000, 5000, 6300, 8000, 10000])        
        self.training.settings.lower_frequencies                                = np.array([14,18,22.4,28,35.5,45,56,71,90,112,140,180,224,280,355,450,560,710,\
                                                                                           900,1120,1400,1800,2240,2800,3550,4500,5600,7100,9000 ])
        self.training.settings.upper_frequencies                                = np.array([18,22.4,28,35.5,45,56,71,90,112,140,180,224,280,355,450,560,710,900,1120,\
                                                                                 1400,1800,2240,2800,3550,4500,5600,7100,9000,11200 ])
   
        
        
        self.training.AoA                             = np.linspace(0,90,7) * Units.deg 
        self.training.Mach                            = np.array([1E-12, 0.25 ,0.5 ,0.75])      
        self.training.RPM                             = np.linspace(0,2500,6)  
        #self.training.blade_pitch                     = np.linspace(0,30,3)
        self.training.distance                        = np.array([50,250,500,1000,5000]) *Units.feet
        self.training.data                            = Conditions()   

        self.surrogates                               = Conditions()  

        # build the evaluation process
        self.process                                  = Process()
        self.process.compute                          = Process()   
        self.process.compute.noise                    = None  
        
        return
            

    def initialize(self):  
        use_surrogate   = self.settings.use_surrogate  

        # If we are using the surrogate

        compute   =  self.process.compute             
        if use_surrogate == True: 
            # sample training data
            train_noise_surrogates(self)

            # build surrogate
            build_noise_surrogates(self)

            compute.noise  = evaluate_noise_surrogate            
        else:
            compute.noise  = evaluate_noise_no_surrogate  
        return 
    
         
    def evaluate_noise(self,state):
        """The default evaluate function.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        results   <RCAIDE data class>

        Properties Used:
        self.settings
        self.geometry
        """          
        settings = self.settings
        geometry = self.geometry 
        results  = self.process.compute(state,settings,geometry)
        
        return results 
    
    