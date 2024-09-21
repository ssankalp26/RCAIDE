# RCAIDE/Library/Methods/Thermal_Management/Liquid_Cooled_Wavy_Channel/pack_wavy_channel_residuals.py
#
# 
# Created:  Sep 2024, S. Shekar 

# ---------------------------------------------------------------------------------------------------------------------- 
#  pack wavy channel heat acqusistion residuals
# ----------------------------------------------------------------------------------------------------------------------  
def pack_wavy_channel_residuals(bus,wavy_channel,battery,segment,coolant_line): 
    battery_conditions  = segment.state.conditions.energy[bus.tag][battery.tag] 
    t_desired           = battery.ideal_operating_temperature
    t_bat               = battery_conditions.cell.temperature
    segment.state.residuals.network[coolant_line.tag + '_' + wavy_channel.tag +  '_temperature'] = t_bat - t_desired
    return 
