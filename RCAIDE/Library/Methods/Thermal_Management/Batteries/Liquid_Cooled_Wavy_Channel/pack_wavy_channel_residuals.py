# RCAIDE/Library/Methods/Thermal_Management/Liquid_Cooled_Wavy_Channel/pack_wavy_channel_residuals.py
#
# 
# Created:  Sep 2024, S. Shekar 

# ---------------------------------------------------------------------------------------------------------------------- 
#  pack wavy channel heat acqusistion residuals
# ----------------------------------------------------------------------------------------------------------------------  
def pack_wavy_channel_residuals(wavy_channel,battery,segment,coolant_line):
    
    coolant_line_results = segment.state.conditions.energy[coolant_line.tag]
    
    
    bus_results   = segment.state.conditions.energy[bus.tag]
    motor         = propulsor.motor
    rotor         = propulsor.rotor 
    q_motor       = bus_results[propulsor.tag][motor.tag].torque
    q_prop        = bus_results[propulsor.tag][rotor.tag].torque 
    segment.state.residuals.network[propulsor.tag  + '_rotor_motor_torque'] = q_motor - q_prop 
    return 
