# RCAIDE/Library/Methods/Propulsors/Turboprop_Propulsor/append_turboprop_conditions.py
# (c) Copyright 2023 Aerospace Research Community LLC
# 
# Created:  Jun 2024, M. Guidotti 

from RCAIDE.Framework.Mission.Common     import   Conditions

# ---------------------------------------------------------------------------------------------------------------------- 
#  append_turboprop_conditions
# ----------------------------------------------------------------------------------------------------------------------    
def append_turboprop_conditions(turboprop,segment,fuel_line,add_additional_network_equation):  
    ones_row    = segment.state.ones_row                  
    segment.state.conditions.energy[fuel_line.tag][turboprop.tag]                                = Conditions()  
    segment.state.conditions.energy[fuel_line.tag][turboprop.tag].throttle                       = 0. * ones_row(1)      
    segment.state.conditions.energy[fuel_line.tag][turboprop.tag].commanded_thrust_vector_angle  = 0. * ones_row(1)  
    segment.state.conditions.energy[fuel_line.tag][turboprop.tag].thrust                         = 0. * ones_row(3) 
    segment.state.conditions.energy[fuel_line.tag][turboprop.tag].power                          = 0. * ones_row(1) 
    segment.state.conditions.energy[fuel_line.tag][turboprop.tag].moment                         = 0. * ones_row(3) 
    segment.state.conditions.energy[fuel_line.tag][turboprop.tag].inputs                         = Conditions()
    segment.state.conditions.energy[fuel_line.tag][turboprop.tag].outputs                        = Conditions() 
    segment.state.conditions.noise[fuel_line.tag][turboprop.tag]                                 = Conditions() 
    segment.state.conditions.noise[fuel_line.tag][turboprop.tag].turboprop                       = Conditions() 
    segment.state.conditions.noise[fuel_line.tag][turboprop.tag].turboprop.core_nozzle           = Conditions() 
    segment.state.conditions.noise[fuel_line.tag][turboprop.tag].turboprop.propeller             = Conditions()  
    return 