# RCAIDE/Library/Methods/Thermal_Management/Liquid_Cooled_Wavy_Channel/unpack_wavy_channel_unknowns.py
#
# 
# Created:  Sep 2024, S. Shekar 

# ---------------------------------------------------------------------------------------------------------------------- 
#  Unpack wavy channel heat acquisition unknowns 
# ----------------------------------------------------------------------------------------------------------------------  
def unpack_wavy_channel_unknowns(wavy_channel,battery, segment,coolant_line):
    coolant_line_results = segment.state.conditions.energy[coolant_line.tag]
    coolant_line_results[wavy_channel.tag].turndown_ratio =  segment.state.unknowns['turndown_ratio']
    return 