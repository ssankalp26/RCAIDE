# RCAIDE/Library/Methods/Thermal_Management/Batteries/Air_Cooled/append_air_cooling_conditions.py
# 
# Created:  Aug 2024, S. Shekar

import RCAIDE
from RCAIDE.Framework.Mission.Common     import   Conditions

# ---------------------------------------------------------------------------------------------------------------------- 
#  append_turbofan_conditions
# ---------------------------------------------------------------------------------------------------------------------- 

def append_reservoir_conditions(reservoir,segment,coolant_line,add_additional_network_equation):
    
    atmosphere    = RCAIDE.Framework.Analyses.Atmospheric.US_Standard_1976()
    alt           = -segment.conditions.frames.inertial.position_vector[:,2] 
    if segment.temperature_deviation != None:
        temp_dev = segment.temperature_deviation    
    atmo_data    = atmosphere.compute_values(altitude = alt,temperature_deviation=temp_dev)    

    ones_row                                                                                        = segment.state.ones_row    
    segment.state.conditions.energy[coolant_line.tag][reservoir.tag]                                 = Conditions()
    segment.state.conditions.energy[coolant_line.tag][reservoir.tag].coolant_temperature             = atmo_data.temperature[0,0]* ones_row(1)       
    return

def append_reservoir_segment_conditions(reservoir,segment,coolant_line,conditions):
    
    reservoir_conditions = conditions[coolant_line.tag][reservoir.tag]
    if segment.state.initials:  
        reservoir_initials                                   = segment.state.initials.conditions.energy[coolant_line.tag][reservoir.tag]
        reservoir_conditions.coolant_temperature[:,0]        = reservoir_initials.coolant_temperature[-1,0] 
    
    return