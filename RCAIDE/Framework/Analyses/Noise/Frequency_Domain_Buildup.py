## @ingroup Analyses-Noise
# RCAIDE/Framework/Analyses/Noise/Frequency_Domain_Buildup.py
# 
# 
# Created:  Jul 2023, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------  
# noise imports    
from .Noise      import Noise 
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
        settings                                        = self.settings
        settings.harmonics                              = np.arange(1,30) 
        settings.flyover                                = False    
        settings.approach                               = False
        settings.sideline                               = False
        settings.sideline_x_position                    = 0 
        settings.print_noise_output                     = False  
        settings.mean_sea_level_altitude                = True 
        settings.aircraft_destination_location          = np.array([0,0,0])
        settings.aircraft_departure_location            = np.array([0,0,0])
        
        settings.topography_file                        = None
        settings.ground_microphone_locations            = None   
        settings.ground_microphone_coordinates          = None
        settings.ground_microphone_x_resolution         = 100
        settings.ground_microphone_y_resolution         = 100
        settings.ground_microphone_x_stencil            = 2
        settings.ground_microphone_y_stencil            = 2
        settings.ground_microphone_min_x                = 1E-6
        settings.ground_microphone_max_x                = 5000 
        settings.ground_microphone_min_y                = 1E-6
        settings.ground_microphone_max_y                = 450  
        
        settings.noise_hemisphere                       = False 
        settings.use_surrogate                          = True        
        settings.noise_hemisphere_radius                = 20 
        settings.noise_hemisphere_microphone_resolution = 20
        settings.noise_hemisphere_phi_angle_bounds      = np.array([0,np.pi])
        settings.noise_hemisphere_theta_angle_bounds    = np.array([0,2*np.pi])
         
                
        # settings for acoustic frequency resolution
        settings.center_frequencies                   = np.array([16,20,25,31.5,40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, \
                                                                  500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150,
                                                                  4000, 5000, 6300, 8000, 10000])        
        settings.lower_frequencies                    = np.array([14,18,22.4,28,35.5,45,56,71,90,112,140,180,224,280,355,450,560,710,\
                                                                  900,1120,1400,1800,2240,2800,3550,4500,5600,7100,9000 ])
        settings.upper_frequencies                    = np.array([18,22.4,28,35.5,45,56,71,90,112,140,180,224,280,355,450,560,710,900,1120,\
                                                                 1400,1800,2240,2800,3550,4500,5600,7100,9000,11200 ])
        
        return
            

    def initialize(self):  
        use_surrogate   = self.settings.use_surrogate  

        # If we are using the surrogate
        if use_surrogate == True: 
            # sample training data
            train_noise_surrogates(self)

            # build surrogate
            build_noise_surrogates(self)  
    
        # build the evaluation process
        compute   =  self.process.compute                  
        if use_surrogate == True: 
            compute.noise  = evaluate_noise_surrogate
        else:
            compute.noise  = evaluate_noise_no_surrogate  
        return 
    
         
    def evaluate(self,state):
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
    
    