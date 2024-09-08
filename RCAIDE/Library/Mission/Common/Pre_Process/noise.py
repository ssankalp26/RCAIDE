## @ingroup Library-Missions-Segments-Common-Pre_Process
# RCAIDE/Library/Missions/Common/Pre_Process/noise.py 
# 
# Created:  Sep 2024, M. Clarke

# ----------------------------------------------------------------------------------------------------------------------
#  IMPORT
# ----------------------------------------------------------------------------------------------------------------------
import  RCAIDE

# ----------------------------------------------------------------------------------------------------------------------
#  noise
# ----------------------------------------------------------------------------------------------------------------------  
## @ingroup Library-Missions-Segments-Common-Pre_Process
def noise(mission):
    """ Runs aerdoynamics model and build surrogate
    
        Assumptions:
            N/A
        
        Inputs:
            None
            
        Outputs:
            None  
    """      
    last_tag = None
    for tag,segment in mission.segments.items():        
        if (type(segment.analyses.noise) == RCAIDE.Framework.Analyses.Noise.Frequency_Domain_Buildup):
            if last_tag and  'compute' in mission.segments[last_tag].analyses.noise.process: 
                segment.analyses.noise.process.compute.noise = mission.segments[last_tag].analyses.noise.process.compute.noise
                segment.analyses.noise.surrogates            = mission.segments[last_tag].analyses.noise.surrogates 
            else:          
                noise   = segment.analyses.noise
                noise.initialize()   
                last_tag = tag  
    return 