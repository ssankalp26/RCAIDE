# digital_elevation_and_noise_hemispheres_test.py
#
# Created: Dec 2023 M. Clarke  
 
# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------
# RCAIDE Imports 
import RCAIDE
from RCAIDE.Framework.Core import Units , Data 
from RCAIDE.Library.Plots import *     
from RCAIDE.Library.Methods.Noise.Metrics import *   

# Python imports
import matplotlib.pyplot as plt  
import sys 
import numpy as np     

# local imports 
sys.path.append('../../Vehicles')
from NASA_X57    import vehicle_setup, configs_setup     

# ----------------------------------------------------------------------
#   Main
# ---------------------------------------------------------------------- 
def main():
    
    noise_surrogate_flag = [False,True]
    
    SPL_true          = np.array([[37.14075542, 42.33414526, 51.94732132, 42.10072163, 37.18022958,
                                   46.0969593 , 47.44623416, 47.93926387, 47.44454783, 46.0978427 ,
                                   42.1620996 , 42.52773202, 42.6525962 , 42.52774501, 42.16243429,
                                   39.11938321, 39.28360082, 39.33895519, 39.28366191, 39.11956757,
                                   36.81426443, 36.90677463, 36.93781584, 36.90682277, 36.81438045]])
    
    SPL_spectrum_true = np.array([[ 7.40728109,  9.34607504, 12.00824407, 15.12069454, 18.36336706,
                                    21.22196768, 59.5919173 , 26.70475275, 28.98571374, 39.99845934,
                                    33.31732641, 35.25543649, 36.91960554, 38.59507584, 40.30003769,
                                    41.74331938, 42.92665033, 43.64231974, 43.79405332, 43.44561005,
                                    42.41272275, 40.84333301, 38.88170669, 36.57541427, 33.90453515,
                                    31.60425981, 27.89347298, 23.62849604, 18.83407496]])
    
    for i in  range(2):
        vehicle  = vehicle_setup()        
        configs  = configs_setup(vehicle) 
        analyses = analyses_setup(configs,noise_surrogate_flag[i])  
        mission  = mission_setup(analyses)
        missions = missions_setup(mission)  
        results  = missions.base_mission.evaluate() 

        SPL          = results.segments.cruise.conditions.noise.total_SPL_dBA[0]
        SPL_spectrum = results.segments.cruise.conditions.noise.total_SPL_1_3_spectrum_dBA[0,2,:]
          
        error_SPL = np.abs((SPL - SPL_true[0])/SPL_true[0])  
        max_SPL_error =  max(error_SPL) 
        print('Max SPL Error: ',max_SPL_error)
        assert max_SPL_error < 1
 
        error_SPL_spectrum     = np.abs((SPL_spectrum - SPL_spectrum_true[0])/SPL_spectrum_true[0])  
        max_SPL_spectrum_error =  max(error_SPL_spectrum) 
        print('Max SPL Error: ',max_SPL_spectrum_error)
        assert max_SPL_spectrum_error < 1          
     
    return      

# ----------------------------------------------------------------------
#   Define the Vehicle Analyses
# ---------------------------------------------------------------------- 
def analyses_setup(configs,noise_surrogate_flag):

    analyses = RCAIDE.Framework.Analyses.Analysis.Container()

    # build a base analysis for each config
    for tag,config in configs.items():
        analysis      = base_analysis(config,noise_surrogate_flag) 
        analyses[tag] = analysis

    return analyses  


def base_analysis(vehicle,noise_surrogate_flag):

    # ------------------------------------------------------------------
    #   Initialize the Analyses
    # ------------------------------------------------------------------     
    analyses = RCAIDE.Framework.Analyses.Vehicle() 
 
    # ------------------------------------------------------------------
    #  Weights
    weights         = RCAIDE.Framework.Analyses.Weights.Weights_eVTOL()
    weights.vehicle = vehicle
    analyses.append(weights)

    # ------------------------------------------------------------------
    #  Aerodynamics Analysis
    aerodynamics          = RCAIDE.Framework.Analyses.Aerodynamics.Vortex_Lattice_Method() 
    aerodynamics.geometry = vehicle
    aerodynamics.settings.drag_coefficient_increment = 0.0000
    analyses.append(aerodynamics)   
 
    #  Noise Analysis   
    noise = RCAIDE.Framework.Analyses.Noise.Frequency_Domain_Buildup()   
    noise.geometry = vehicle
    noise.settings.use_surrogate = noise_surrogate_flag 
    noise.settings.ground_microphone_min_x   = 1E-6
    noise.settings.ground_microphone_max_x   = 1000 
    noise.settings.ground_microphone_min_y   = -100  
    noise.settings.ground_microphone_max_y   =  100   
    analyses.append(noise)

    # ------------------------------------------------------------------
    #  Energy
    energy          = RCAIDE.Framework.Analyses.Energy.Energy()
    energy.vehicle  = vehicle 
    analyses.append(energy)

    # ------------------------------------------------------------------
    #  Planet Analysis
    planet = RCAIDE.Framework.Analyses.Planets.Planet()
    analyses.append(planet)

    # ------------------------------------------------------------------
    #  Atmosphere Analysis
    atmosphere = RCAIDE.Framework.Analyses.Atmospheric.US_Standard_1976()
    atmosphere.features.planet = planet.features
    analyses.append(atmosphere)   

    # done!
    return analyses    

# ----------------------------------------------------------------------
#  Set Up Mission 
# ---------------------------------------------------------------------- 
def mission_setup(analyses):      
    
    # ------------------------------------------------------------------
    #   Initialize the Mission
    # ------------------------------------------------------------------
    mission       = RCAIDE.Framework.Mission.Sequential_Segments()
    mission.tag   = 'mission' 
    Segments      = RCAIDE.Framework.Mission.Segments  
    base_segment  = Segments.Segment()   
    base_segment.state.numerics.number_of_control_points = 5
    base_segment.state.numerics.discretization_method    = RCAIDE.Library.Methods.Utilities.Chebyshev.linear_data
    
    # ------------------------------------------------------------------
    #   Departure End of Runway Segment Flight 1 : 
    # ------------------------------------------------------------------ 

    segment = Segments.Cruise.Constant_Speed_Constant_Altitude(base_segment) 
    segment.tag = "cruise"   
    segment.analyses.extend( analyses.base ) 
    segment.initial_battery_state_of_charge              = 1.0
    segment.distance                                     = 1000    
    segment.altitude                                     = 50.0   
    segment.air_speed                                    = 100.   * Units['mph']       
    
    # define flight dynamics to model 
    segment.flight_dynamics.force_x                      = True  
    segment.flight_dynamics.force_z                      = True     
    
    # define flight controls 
    segment.assigned_control_variables.throttle.active               = True           
    segment.assigned_control_variables.throttle.assigned_propulsors  = [['starboard_propulsor','port_propulsor']] 
    segment.assigned_control_variables.body_angle.active             = True                
       
    mission.append_segment(segment)  
     
    return mission

# ----------------------------------------------------------------------
#  Set Up Missions 
# ---------------------------------------------------------------------- 
def missions_setup(mission): 
 
    missions     = RCAIDE.Framework.Mission.Missions() 
    mission.tag  = 'base_mission'
    missions.append(mission)
 
    return missions  


# ----------------------------------------------------------------------
#  Plot Resuls 
# ---------------------------------------------------------------------- 
def plot_results(results,regression_plotting_flag): 
    
    noise_data   = post_process_noise_data(results)   
    return  

if __name__ == '__main__': 
    main()    
    plt.show()
